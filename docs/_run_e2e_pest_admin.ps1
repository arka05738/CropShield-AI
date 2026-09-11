$ErrorActionPreference = 'Continue'
$base7 = 'http://127.0.0.1:8007/api/v1'
$base5 = 'http://127.0.0.1:8005/api/v1'
$imgPath = 'C:\Users\ARKA\Downloads\crop_Project_SIH\Backend\uploads\_e2e_leaf.jpg'
$outDir = 'C:\Users\ARKA\Downloads\crop_Project_SIH\docs'

function Get-HttpCode([string]$raw) {
  if ($raw -match 'HTTPCODE:(\d+)') { return $Matches[1] }
  return '?'
}
function Get-Body([string]$raw) {
  return ($raw -replace '\|HTTPCODE:\d+$', '')
}

try {
  $h = Invoke-RestMethod "$base7/health"
  Write-Output "8007 $($h.status) pest=$($h.pest_inference) model=$($h.pest_model_id)"
} catch {
  Write-Output "8007 down, starting..."
  docker start cropshield-backend-e2e | Out-Null
  Start-Sleep 12
  $h = Invoke-RestMethod "$base7/health"
  Write-Output "8007 $($h.status) pest=$($h.pest_inference)"
}

$farmer = Invoke-RestMethod -Uri "$base7/auth/login" -Method POST -ContentType 'application/json' -Body '{"email":"e2e.farmer@cropshield.ai","password":"cropshield123"}'
$token = $farmer.access_token
Write-Output "PEST_LOGIN $($farmer.user.email) $($farmer.user.role)"

$sw = [Diagnostics.Stopwatch]::StartNew()
$raw = & curl.exe -s -w '|HTTPCODE:%{http_code}' -X POST "$base7/pests/detect" -H "Authorization: Bearer $token" -F "file=@${imgPath};type=image/jpeg" -F 'crop_hint=Tomato'
$sw.Stop()
$http = Get-HttpCode $raw
$body = Get-Body $raw
Set-Content -Path "$outDir\_e2e_pest_result.json" -Value $body
$j = $body | ConvertFrom-Json
Write-Output "PEST http=$http status=$($j.status) count=$($j.count) severity=$($j.severity) model=$($j.model.model_id) dets=$($j.detections.Count) guidance=$($j.advisory.guidance_available) ms=$($sw.ElapsedMilliseconds)"
if ($j.detections -and $j.detections.Count -gt 0) {
  $j.detections | Select-Object -First 3 | ForEach-Object {
    Write-Output ("DET pest={0} conf={1} bbox={2}" -f $_.pest, $_.confidence, ($_.bbox | ConvertTo-Json -Compress))
  }
} else {
  Write-Output 'REAL MODEL EXECUTED — ZERO DETECTIONS'
}

$ph = Invoke-RestMethod -Uri "$base7/pests/history" -Headers @{ Authorization = "Bearer $token" }
Write-Output "PEST_HISTORY count=$($ph.count) items=$($ph.items.Count)"

$f5 = Invoke-RestMethod -Uri "$base5/auth/login" -Method POST -ContentType 'application/json' -Body '{"email":"demo@cropshield.ai","password":"cropshield123"}'
$t5 = $f5.access_token

$rawU = & curl.exe -s -w '|HTTPCODE:%{http_code}' -X POST "$base5/diagnose" -H "Authorization: Bearer $t5" -F "file=@${imgPath};type=image/jpeg" -F 'crop_hint=Millet'
$jU = (Get-Body $rawU) | ConvertFrom-Json
Write-Output "UNSUPPORTED_MILLET http=$(Get-HttpCode $rawU) status=$($jU.status) disease=$($jU.disease.disease)"

$rawA = & curl.exe -s -w '|HTTPCODE:%{http_code}' -X POST "$base5/diagnose" -F "file=@${imgPath};type=image/jpeg" -F 'crop_hint=Grape'
Write-Output "NO_AUTH_DIAGNOSE http=$(Get-HttpCode $rawA)"

$bad = "$outDir\_e2e_corrupt.jpg"
[IO.File]::WriteAllBytes($bad, [byte[]](1..40))
$rawC = & curl.exe -s -w '|HTTPCODE:%{http_code}' -X POST "$base5/diagnose" -H "Authorization: Bearer $t5" -F "file=@${bad};type=image/jpeg" -F 'crop_hint=Grape'
$cBody = Get-Body $rawC
$snip = if ($cBody.Length -gt 160) { $cBody.Substring(0, 160) } else { $cBody }
Write-Output "CORRUPT http=$(Get-HttpCode $rawC) snip=$snip"

try {
  Invoke-WebRequest -Uri "$base5/admin/analytics" -Headers @{ Authorization = "Bearer $t5" } -UseBasicParsing | Out-Null
  Write-Output 'FARMER_ADMIN unexpected 200'
} catch {
  Write-Output "FARMER_ADMIN $($_.Exception.Response.StatusCode.value__)"
}

$a5 = Invoke-RestMethod -Uri "$base5/auth/login" -Method POST -ContentType 'application/json' -Body '{"email":"admin@cropshield.ai","password":"cropshield123"}'
$an = Invoke-RestMethod -Uri "$base5/admin/analytics" -Headers @{ Authorization = "Bearer $($a5.access_token)" }
Write-Output "ADMIN_ANALYTICS analyses=$($an.total_analyses) disease=$($an.disease_cases) pest=$($an.pest_cases) farmers=$($an.total_farmers)"
$cases = Invoke-RestMethod -Uri "$base5/admin/cases" -Headers @{ Authorization = "Bearer $($a5.access_token)" }
Write-Output "ADMIN_CASES count=$($cases.count)"
$models = Invoke-RestMethod -Uri "$base5/admin/models" -Headers @{ Authorization = "Bearer $($a5.access_token)" }
Write-Output "ADMIN_MODELS count=$($models.count)"
$users = Invoke-RestMethod -Uri "$base5/admin/users" -Headers @{ Authorization = "Bearer $($a5.access_token)" }
Write-Output "ADMIN_USERS count=$($users.count)"

$hist = Invoke-RestMethod -Uri "$base5/analysis/history" -Headers @{ Authorization = "Bearer $t5" }
$items = if ($hist.items) { $hist.items } else { @($hist) }
Write-Output "OWN_HISTORY $($items.Count)"
$otherCase = @($cases.cases) | Where-Object { $_.user_id -and $_.user_id -ne $f5.user.id } | Select-Object -First 1
if ($otherCase) {
  try {
    $r = Invoke-WebRequest -Uri "$base5/analysis/$($otherCase.id)" -Headers @{ Authorization = "Bearer $t5" } -UseBasicParsing
    Write-Output "CROSS_FARMER_GET $($r.StatusCode) UNEXPECTED"
  } catch {
    Write-Output "CROSS_FARMER_GET $($_.Exception.Response.StatusCode.value__)"
  }
} else {
  Write-Output 'CROSS_FARMER_GET SKIP'
}

# backend unavailable friendly check later via frontend
# health secrets
$health = Invoke-RestMethod "$base5/health"
$healthJson = $health | ConvertTo-Json -Depth 6
$secretLeak = $healthJson -match 'JWT|mongo.*pass|hf_token|sk-|Bearer '
Write-Output "HEALTH_SECRET_LEAK=$secretLeak"

# persistence: count analyses in mongo
docker exec cropshield-mongodb mongosh cropshield --quiet --eval "print('mongo_analyses='+db.analyses.countDocuments({})); print('mongo_pest='+db.pest_analyses.countDocuments({}))"
