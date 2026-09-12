NEW_RECORDS = [
    {
        "id": "icar_pop_tomato_septoria_leaf_spot",
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "pest": "Aphid / Whitefly Vector",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Package of Practices for Commercial Solanaceous Crops - Foliar Spot & Blight Management",
        "page_number": 46,
        "condition_summary": "Septoria lycopersici fungal leaf spot characterized by circular brown margins, sunken grey-white centres dotted with dark pycnidia, starting on lower leaves during warm, humid weather.",
        "pesticide": {
            "active_ingredient": "Chlorothalonil 75% WP",
            "chemical_name": "Kavach / Bravo 75 WP",
            "exact_dose_per_liter": "2.0 g/L",
            "withholding_period_days": 7,
            "application_method": "High-volume foliar spray ensuring uniform wetting of lower and upper leaf canopies with calibrated hollow-cone nozzle.",
            "safety_warnings": [
                "Wear protective eyewear, gloves, and mask during mixing and spraying.",
                "Do not spray during high midday temperatures or intense sunlight.",
                "Observe mandatory 7-day withholding interval prior to fruit picking."
            ]
        },
        "fertilizer": {
            "n_ratio": "Reduced Nitrogen (-25%)",
            "p_ratio": "Standard Phosphorus (SSP @ 50 kg/ha)",
            "k_ratio": "Elevated Potassium (+25% via SOP 0:0:50 @ 5 g/L foliar)",
            "micronutrients": ["Zinc Sulphate 0.5%", "Borax 0.2% foliar spray"],
            "instructions": "Limit succulent vegetative growth by moderating urea top-dressing. Apply Potassium Sulphate (0:0:50) foliar spray @ 5 g/L to thicken epidermal cell walls against fungal hyphae penetration."
        },
        "ipm": {
            "cultural": [
                "Promptly prune and burn bottom infected leaves showing pycnidia spots (strict field sanitation).",
                "Ensure 60 x 45 cm row spacing to optimize sunlight penetration and rapid dew drying.",
                "Employ drip irrigation or furrow watering; avoid overhead sprinkler watering to prevent spore splash."
            ],
            "biological": [
                "Foliar bio-spray of Trichoderma viride or T. harzianum @ 5 g/L in early morning.",
                "Apply Pseudomonas fluorescens (2% WP) @ 10 g/L for systemic acquired resistance induction.",
                "Neem seed kernel extract (NSKE 5%) @ 50 ml/L to deter insect vectors."
            ],
            "mechanical": [
                "Stake plants with bamboo supports to keep lower foliage off damp ground.",
                "Install yellow sticky traps @ 15-20 traps/acre to monitor vector populations."
            ],
            "chemical": [
                "Foliar spray with Chlorothalonil 75 WP @ 2.0 g/L or Mancozeb 75 WP @ 2.5 g/L at first appearance of circular leaf spots.",
                "For rapidly spreading lesions, rotate with Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply calibrated foliar fungicide spray; remove and bury heavily spotted lower leaves.",
            "day_3": "Check treated foliage to verify arrest of spot expansion and lack of active fungal halo.",
            "day_7": "Inspect 20 random plants across the field; verify that middle and top leaves remain spotless.",
            "day_14": "Evaluate new canopy flush; confirm clean new vegetative growth and healthy blossoming."
        }
    },
    {
        "id": "icar_pop_tomato_bacterial_spot",
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "pest": "Thrips / Whitefly",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "ICAR Guidelines for Bacterial Spot and Wilt Control in Solanaceous Vegetables",
        "page_number": 34,
        "condition_summary": "Xanthomonas perforans small, water-soaked dark brown circular spots surrounded by conspicuous yellow haloes on foliage and scabby raised spots on fruit.",
        "pesticide": {
            "active_ingredient": "Streptocycline 90:10 + Copper Oxychloride 50% WP",
            "chemical_name": "Streptocycline + Blitox 50 WP",
            "exact_dose_per_liter": "0.1 g/L (Streptocycline) + 2.5 g/L (Blitox)",
            "withholding_period_days": 7,
            "application_method": "Foliar spray with fine hollow-cone nozzle to achieve thorough coverage of stems and leaves.",
            "safety_warnings": [
                "Do not apply copper sprays during extreme heat or humidity above 95% to avoid phytotoxicity.",
                "Always premix Streptocycline in a separate small container before adding to the spray tank."
            ]
        },
        "fertilizer": {
            "n_ratio": "Suspend top-dressed Nitrogen",
            "p_ratio": "Standard Phosphorus (50 kg/ha)",
            "k_ratio": "Potassium Schoenite @ 5 g/L foliar",
            "micronutrients": ["Borax 0.1%", "Calcium Nitrate 0.5%"],
            "instructions": "Avoid excess urea top-dressing. Apply Calcium Nitrate @ 5 g/L + Boron 0.1% to strengthen cell walls against bacterial pectolytic enzymes."
        },
        "ipm": {
            "cultural": [
                "Use certified pathogen-free seeds treated with hot water (50°C for 25 minutes).",
                "Dip seedlings in Pseudomonas fluorescens solution (10 g/L) before transplanting.",
                "Avoid working in field when foliage is wet from rain or dew to prevent mechanical bacterial spread."
            ],
            "biological": [
                "Seedling root dip and foliar application of Pseudomonas fluorescens (2% WP) @ 10 g/L.",
                "Bacillus subtilis @ 5 g/L foliar spray."
            ],
            "mechanical": [
                "Disinfect pruning secateurs and shears with 10% sodium hypochlorite solution.",
                "Destroy and bury severely infected crop residue."
            ],
            "chemical": [
                "Spray Streptocycline @ 0.1 g/L combined with Copper Oxychloride 50 WP @ 2.5 g/L at 10-day intervals."
            ]
        },
        "monitoring": {
            "day_1": "Apply combined bactericide-copper protective spray across canopy.",
            "day_3": "Check lesion margins to confirm drying out without yellow chlorotic halo progression.",
            "day_7": "Survey new leaf emergence for clean, unblemished foliage.",
            "day_14": "Inspect fruit clusters for absence of raised bacterial scabs."
        }
    },
    {
        "id": "icar_pop_tomato_late_blight",
        "crop": "Tomato",
        "disease": "Late Blight",
        "pest": "Flea Beetle",
        "authority": "ICAR-Central Potato Research Institute (CPRI) & ICAR-IIHR",
        "document_title": "National Protocol for Late Blight Forewarning & Containment",
        "page_number": 18,
        "condition_summary": "Phytophthora infestans water-soaked greasy olive-green to dark brown lesions with white fuzzy mycelial sporulation on leaf undersides under cool, misty conditions.",
        "pesticide": {
            "active_ingredient": "Cymoxanil 8% + Mancozeb 64% WP",
            "chemical_name": "Curzate M-8 / Sectin",
            "exact_dose_per_liter": "2.5 g/L",
            "withholding_period_days": 5,
            "application_method": "High-volume foliar spray ensuring complete coverage of leaf undersides where sporulation is concentrated.",
            "safety_warnings": [
                "Spray immediately at the first sign of weather forewarning (RH > 85%, temp 12-22°C).",
                "Alternate modes of action to prevent systemic fungicide resistance."
            ]
        },
        "fertilizer": {
            "n_ratio": "Withhold all Nitrogen applications",
            "p_ratio": "Maintain basal Phosphorus",
            "k_ratio": "Elevated Potassium (SOP @ 5 g/L)",
            "micronutrients": ["Potassium Phosphite 40% @ 2 ml/L"],
            "instructions": "Withhold nitrogen top-dressing; apply Potassium Phosphite foliar spray @ 2 ml/L to trigger systemic phytoalexin production."
        },
        "ipm": {
            "cultural": [
                "Destroy volunteer solanaceous hosts and cull piles near the field.",
                "Ensure wide row spacing (75 x 60 cm) to maximize air movement through the lower canopy.",
                "Irrigate only via drip lines in early morning; never irrigate in late afternoon."
            ],
            "biological": [
                "Prophylactic bio-spray of Trichoderma harzianum @ 5 g/L before onset of misty weather.",
                "Apply bio-agent Bacillus amyloliquefaciens @ 5 ml/L."
            ],
            "mechanical": [
                "Carefully remove blighted shoots in plastic bags and destroy off-site.",
                "Avoid harvesting wet fruit."
            ],
            "chemical": [
                "Prophylactic: Mancozeb 75 WP @ 2.5 g/L.",
                "Curative: Cymoxanil 8% + Mancozeb 64% WP @ 2.5 g/L or Dimethomorph 50 WP @ 1.0 g/L or Fenamidone 10% + Mancozeb 50% WG @ 2.5 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply systemic curative spray; remove sporulating primary focus patches.",
            "day_3": "Check lesions for desiccation of white sporulation fringe on lower leaf surfaces.",
            "day_7": "Re-scout entire field border and low-lying damp areas for secondary spread.",
            "day_14": "Verify clean developing fruit clusters and absence of brown greasy rot."
        }
    },
    {
        "id": "icar_pop_tomato_leaf_mold",
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "pest": "Whitefly",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Protected & Open-Field Solanaceous Crop Disease Protocols",
        "page_number": 52,
        "condition_summary": "Passalora fulva (Cladosporium fulvum) pale yellow chlorotic patches on upper leaf surfaces matching olive-green velvety fungal down on corresponding undersides under humid canopy conditions.",
        "pesticide": {
            "active_ingredient": "Carbendazim 12% + Mancozeb 63% WP",
            "chemical_name": "Saaf / Companion 75 WP",
            "exact_dose_per_liter": "2.0 g/L",
            "withholding_period_days": 10,
            "application_method": "Targeted underside foliar spray using hollow-cone nozzle.",
            "safety_warnings": [
                "Do not exceed two consecutive applications of triazole or benzimidazole fungicides."
            ]
        },
        "fertilizer": {
            "n_ratio": "Moderate Nitrogen (-20%)",
            "p_ratio": "Standard Phosphorus (50 kg/ha)",
            "k_ratio": "Potassium Sulphate (SOP) @ 5 g/L",
            "micronutrients": ["Calcium Silicate @ 2 g/L"],
            "instructions": "Apply Calcium Silicate foliar spray @ 2 g/L to reinforce the cuticular layer against fungal appressorial penetration."
        },
        "ipm": {
            "cultural": [
                "Prune lower senescent leaves (bottom 30 cm) to enhance horizontal air circulation.",
                "Reduce planting density to ensure canopy stays dry."
            ],
            "biological": [
                "Bacillus subtilis @ 5 g/L foliar spray.",
                "Pseudomonas fluorescens @ 10 g/L."
            ],
            "mechanical": [
                "Improve greenhouse ventilation using exhaust fans and roof louvers."
            ],
            "chemical": [
                "Spray Carbendazim + Mancozeb @ 2.0 g/L or Difenoconazole 25 EC @ 0.5 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply protective underside spray; perform lower canopy de-leafing.",
            "day_3": "Check olive-green fungal down on leaf undersides for drying and browning.",
            "day_7": "Examine upper canopy for absence of new chlorotic patches.",
            "day_14": "Confirm vigorous terminal shoot expansion."
        }
    },
    {
        "id": "icar_pop_tomato_target_spot",
        "crop": "Tomato",
        "disease": "Target Spot",
        "pest": "Thrips",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Emerging Foliar Pathogens of Tomato in India - Diagnostic and POP Guide",
        "page_number": 27,
        "condition_summary": "Corynespora cassiicola pinpoint brown spots expanding to circular target lesions with concentric rings, yellow haloes, and defoliation.",
        "pesticide": {
            "active_ingredient": "Azoxystrobin 23% SC",
            "chemical_name": "Amistar 23 SC / Mirador",
            "exact_dose_per_liter": "1.0 ml/L",
            "withholding_period_days": 5,
            "application_method": "Thorough canopy spray ensuring droplet coverage across upper and lower canopy layers.",
            "safety_warnings": [
                "Do not tank-mix with EC formulations or organosilicone surfactants."
            ]
        },
        "fertilizer": {
            "n_ratio": "Balanced Nitrogen",
            "p_ratio": "Standard Phosphorus",
            "k_ratio": "Potassium Nitrate (13:0:45) @ 5 g/L",
            "micronutrients": ["Zinc 0.5%", "Boron 0.1%"],
            "instructions": "Apply Potassium Nitrate (13:0:45) foliar spray @ 5 g/L to enhance leaf resilience during flowering and fruit sizing."
        },
        "ipm": {
            "cultural": ["Crop rotation with non-solanaceous crops; deep summer ploughing; plastic mulching."],
            "biological": ["Trichoderma harzianum @ 5 g/L; Pseudomonas fluorescens @ 10 g/L."],
            "mechanical": ["Removal and burning of severely spotted branches."],
            "chemical": ["Azoxystrobin 23 SC @ 1.0 ml/L or Chlorothalonil 75 WP @ 2.0 g/L."]
        },
        "monitoring": {
            "day_1": "Apply strobilurin fungicide spray; remove heavily spotted lower leaves.",
            "day_3": "Verify that lesion margins have ceased expanding.",
            "day_7": "Survey newly emerged leaves for zero lesion spotting.",
            "day_14": "Inspect fruit calyxes and fruit skin."
        }
    },
    {
        "id": "icar_pop_tomato_tylcv",
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus",
        "pest": "Whitefly (Bemisia tabaci)",
        "authority": "ICAR-National Bureau of Agricultural Insect Resources (NBAIR) & ICAR-IIHR",
        "document_title": "Integrated Management of Whitefly-Transmitted Geminiviruses in Horticultural Crops",
        "page_number": 15,
        "condition_summary": "Upward leaf cupping, conspicuous interveinal chlorosis, stunted bushy terminal shoots, and flower drop vectored by Bemisia tabaci whiteflies.",
        "pesticide": {
            "active_ingredient": "Diafenthiuron 50% WP",
            "chemical_name": "Pegasus 50 WP / Polo",
            "exact_dose_per_liter": "1.2 g/L",
            "withholding_period_days": 7,
            "application_method": "Directed underside foliar spray targeting whitefly nymphs and adults on young tender foliage.",
            "safety_warnings": [
                "Wear protective clothing; avoid spraying during active honeybee foraging hours."
            ]
        },
        "fertilizer": {
            "n_ratio": "Standard Nitrogen in split applications",
            "p_ratio": "Basal DAP @ 50 kg/ha",
            "k_ratio": "Potassium Nitrate @ 5 g/L foliar",
            "micronutrients": ["Zinc Sulphate 0.5%", "Ferrous Sulphate 0.2%", "Borax 0.1%"],
            "instructions": "Apply multi-micronutrient spray (Zn, Fe, B) + 19:19:19 @ 5 g/L to stimulate vegetative growth and overcome viral stunting."
        },
        "ipm": {
            "cultural": [
                "Plant 2-3 border rows of tall barrier crops like maize, jowar, or bajra 30 days prior to transplanting.",
                "Rogue out and destroy infected viral symptomatic plants within 4 weeks of transplanting.",
                "Silver or yellow reflective mulch to repel settling whiteflies."
            ],
            "biological": [
                "Spray Neem Oil 10,000 ppm @ 2 ml/L or NSKE 5% @ 50 ml/L.",
                "Release predators Chrysoperla carnea @ 10,000/ha."
            ],
            "mechanical": [
                "Install yellow sticky traps @ 25 traps/acre at canopy height for mass trapping of whiteflies."
            ],
            "chemical": [
                "Spray Diafenthiuron 50 WP @ 1.2 g/L or Thiamethoxam 25 WG @ 0.3 g/L or Spiromesifen 22.9 SC @ 1.0 ml/L to control vector."
            ]
        },
        "monitoring": {
            "day_1": "Install yellow sticky traps; spray vector-control insecticide.",
            "day_3": "Count whiteflies per leaf on 10 random plants; verify population suppression.",
            "day_7": "Rogue out any newly displaying stunted viral plants.",
            "day_14": "Inspect trap catches; re-apply alternate mode of action if counts exceed 5 whiteflies/trap/day."
        }
    },
    {
        "id": "icar_pop_tomato_mosaic_virus",
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus",
        "pest": "Aphids / Mechanical Transmission",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Solanaceous Viral Disease Management Standards - Prevention and Containment",
        "page_number": 22,
        "condition_summary": "Tomato Mosaic Tobamovirus (ToMV) mottled dark-green and light-yellow mosaic pattern on foliage, leaf curling/distortion (shoestringing), and stunted internodes mechanically transmitted.",
        "pesticide": {
            "active_ingredient": "Trisodium Phosphate 10% (Seed/Tool Decontamination) + Skimmed Milk 10%",
            "chemical_name": "TSP Seed & Tool Wash + Milk Foliar Spray",
            "exact_dose_per_liter": "100 g/L (TSP tool wash) / 100 ml/L (fresh skimmed milk foliar)",
            "withholding_period_days": 0,
            "application_method": "Tools: dip in 10% TSP solution between rows. Foliar: spray 10% skimmed milk suspension to neutralize mechanical virion transmission.",
            "safety_warnings": [
                "No synthetic antiviral chemical curative exists; containment relies on strict hygiene and vector suppression."
            ]
        },
        "fertilizer": {
            "n_ratio": "Balanced Nitrogen (avoid excess)",
            "p_ratio": "Standard Phosphorus",
            "k_ratio": "Elevated Potassium (SOP @ 5 g/L)",
            "micronutrients": ["Zinc Sulphate 0.5%", "Amino Acid foliar @ 2 ml/L"],
            "instructions": "Apply Amino Acid bio-stimulant @ 2 ml/L + 19:19:19 @ 5 g/L to support metabolic vitality and mitigate yield loss."
        },
        "ipm": {
            "cultural": [
                "Wash hands with soap and water or 10% TSP before handling seedlings.",
                "Rogue out and burn infected mosaic-affected plants immediately.",
                "Do not smoke or use tobacco products near tomato crops."
            ],
            "biological": [
                "Seed treatment with Pseudomonas fluorescens @ 10 g/kg seed.",
                "Spray 10% reconstituted skimmed milk suspension prior to transplanting."
            ],
            "mechanical": [
                "Sterilize pruning tools in 10% TSP solution between plants."
            ],
            "chemical": [
                "Control potential aphid vectors with Neem Oil 1500 ppm @ 3 ml/L or Thiamethoxam 25 WG @ 0.3 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Identify and carefully rogue out mosaic-infected plants; dip pruning tools in disinfectant.",
            "day_3": "Check adjacent plants for mechanical transmission symptoms.",
            "day_7": "Inspect young terminal leaves for normal non-mottled expansion.",
            "day_14": "Assess crop vigour and fruit setting."
        }
    },
    {
        "id": "icar_pop_tomato_spider_mites",
        "crop": "Tomato",
        "disease": "Two-spotted Spider Mite",
        "pest": "Two-spotted Spider Mite (Tetranychus urticae)",
        "authority": "ICAR-National Bureau of Agricultural Insect Resources (NBAIR), Bengaluru",
        "document_title": "Acarine Pests of Vegetable Crops and Management Guidelines",
        "page_number": 39,
        "condition_summary": "Tetranychus urticae chlorotic stippling, bronzing on upper leaf surface, fine silken webbing on leaf undersides, and premature drying during dry, warm weather.",
        "pesticide": {
            "active_ingredient": "Spiromesifen 22.9% SC",
            "chemical_name": "Oberon 240 SC",
            "exact_dose_per_liter": "1.0 ml/L",
            "withholding_period_days": 5,
            "application_method": "High-volume foliar spray directed strictly onto leaf undersides where mite colonies and webbing reside.",
            "safety_warnings": [
                "Ensure spray reaches inside dense plant canopies.",
                "Do not use pyrethroid insecticides which eliminate predatory mites and trigger mite flare-ups."
            ]
        },
        "fertilizer": {
            "n_ratio": "Reduce Nitrogen (-30%)",
            "p_ratio": "Standard Phosphorus",
            "k_ratio": "Potassium Sulphate (0:0:50) @ 5 g/L",
            "micronutrients": ["Sulphur 80% WDG @ 3 g/L"],
            "instructions": "Avoid excess urea fertilization which increases amino acid content of foliage and accelerates mite reproduction. Apply Sulphur 80 WDG @ 3 g/L as dual nutrient and acaricide."
        },
        "ipm": {
            "cultural": [
                "Maintain adequate field soil moisture via regular drip irrigation.",
                "Use overhead water misting in early morning to raise canopy humidity and disrupt mite webbing."
            ],
            "biological": [
                "Release predatory phytoseiid mites (Amblyseius longispinosus or Neoseiulus longispinosus) @ 10 mites/plant.",
                "Foliar spray of entomopathogenic fungus Beauveria bassiana or Hirsutella thompsonii @ 5 g/L."
            ],
            "mechanical": [
                "Prune and destroy heavily webbed lower leaves."
            ],
            "chemical": [
                "Spray Spiromesifen 22.9 SC @ 1.0 ml/L or Propargite 57 EC @ 2.0 ml/L or Fenpyroximate 5 EC @ 1.0 ml/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply thorough underside acaricidal spray; wash canopy with clean water misting.",
            "day_3": "Examine leaf undersides with 10x hand lens; verify cessation of mite crawling activity.",
            "day_7": "Check for newly hatched mite nymphs; evaluate need for second spray.",
            "day_14": "Inspect young foliage for healthy green coloration and absence of stippling."
        }
    },
    {
        "id": "icar_pop_tomato_healthy_gap",
        "crop": "Tomato",
        "disease": "Healthy Crop",
        "pest": "Routine Scouting",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Good Agricultural Practices (GAP) & Preventive Plant Health in Tomato",
        "page_number": 10,
        "condition_summary": "Vigorous, unblemished green foliage, balanced vegetative and reproductive development, and zero detectable pathogenic foliar spots or sucking pest colonies.",
        "pesticide": {
            "active_ingredient": "Pseudomonas fluorescens 2% WP (Prophylactic Bio-protectant)",
            "chemical_name": "Bio-Shield / Bio-Cure",
            "exact_dose_per_liter": "5.0 g/L",
            "withholding_period_days": 0,
            "application_method": "Prophylactic canopy misting in early morning or late evening. Zero chemical pesticides required.",
            "safety_warnings": [
                "Keep biopesticides away from direct sunlight; store in cool, dry storage.",
                "Maintain natural predator populations by avoiding unnecessary prophylactic chemical sprays."
            ]
        },
        "fertilizer": {
            "n_ratio": "Standard balanced N-P-K (120:80:100 kg/ha split)",
            "p_ratio": "Single Super Phosphate 60 kg/ha basal",
            "k_ratio": "Potassium Sulphate (SOP) @ 4 g/L foliar at fruit set",
            "micronutrients": ["Calcium Nitrate 0.5%", "Borax 0.1%", "Zinc Sulphate 0.5%"],
            "instructions": "Maintain balanced fertigation with 19:19:19 @ 3-4 g/L. Apply Calcium-Boron foliar spray during flowering to prevent blossom end rot and maximize fruit quality."
        },
        "ipm": {
            "cultural": [
                "Maintain drip irrigation schedule based on evapo-transpiration requirements.",
                "Weed management to eliminate alternate pest and pathogen hosts.",
                "Ensure proper staking and training of indeterminate tomato varieties."
            ],
            "biological": [
                "Prophylactic foliar spray of Trichoderma harzianum @ 5 g/L every 21 days.",
                "Conserve ladybird beetles, hoverflies, and spiders in the field boundary."
            ],
            "mechanical": [
                "Erect yellow and blue sticky traps (10 traps/acre) for baseline vector monitoring.",
                "Bird perches @ 10/acre."
            ],
            "chemical": [
                "Zero chemical pesticides required for healthy crops. Continue regular weekly scouting."
            ]
        },
        "monitoring": {
            "day_1": "Perform routine weekly field walk; verify healthy leaf turgor and dark green color.",
            "day_3": "Check yellow sticky traps for any early arrivals of whiteflies or aphids.",
            "day_7": "Inspect lower canopy leaves for early signs of senescence or soil-borne splash.",
            "day_14": "Assess blossom clusters and fruit load; maintain scheduled fertigation."
        }
    },
    {
        "id": "icar_pop_potato_early_blight",
        "crop": "Potato",
        "disease": "Early Blight",
        "pest": "Aphid",
        "authority": "ICAR-Central Potato Research Institute (CPRI), Shimla",
        "document_title": "Package of Practices for Potato Cultivation - Foliar Blight Containment",
        "page_number": 33,
        "condition_summary": "Alternaria solani dark brown to black concentric target-ring lesions on older potato leaves, spreading upward during alternating wet and dry canopy conditions.",
        "pesticide": {
            "active_ingredient": "Mancozeb 75% WP",
            "chemical_name": "Dithane M-45 / Indofil M-45",
            "exact_dose_per_liter": "2.5 g/L",
            "withholding_period_days": 10,
            "application_method": "High-volume foliar spray with hollow-cone nozzles covering entire plant foliage.",
            "safety_warnings": [
                "Apply at first sign of concentric spots on lower canopy leaves.",
                "Observe 10-day pre-harvest withholding period."
            ]
        },
        "fertilizer": {
            "n_ratio": "Balanced Nitrogen (avoid late nitrogen top-dressing)",
            "p_ratio": "SSP 60 kg/ha basal",
            "k_ratio": "Potassium Sulphate (SOP) @ 5 g/L foliar",
            "micronutrients": ["Zinc Sulphate 21% @ 25 kg/ha basal"],
            "instructions": "Ensure adequate potassium nutrition at earthing up to enhance tuber quality and foliar resistance against Alternaria blight."
        },
        "ipm": {
            "cultural": [
                "Crop rotation with cereals or legumes (minimum 2-year rotation).",
                "Ensure good drainage and prevent standing water in potato furrows.",
                "Dehaulm (cut foliage) 10-12 days prior to harvest to prevent tuber contamination."
            ],
            "biological": [
                "Foliar spray of Trichoderma harzianum @ 5 g/L in early morning.",
                "Pseudomonas fluorescens @ 10 g/L."
            ],
            "mechanical": [
                "Destroy infected potato haulm residue after harvest."
            ],
            "chemical": [
                "Mancozeb 75 WP @ 2.5 g/L or Chlorothalonil 75 WP @ 2.0 g/L. For severe infection, alternate with Tebuconazole 50% + Trifloxystrobin 25% WG @ 0.6 g/L."
            ]
        },
        "monitoring": {
            "day_1": "Apply calibrated fungicide spray; inspect bottom leaves.",
            "day_3": "Check target spots to verify lack of chlorotic halo progression.",
            "day_7": "Inspect 20 plants per quadrant across the potato field.",
            "day_14": "Assess tuber bulking and verify clean upper foliage."
        }
    },
    {
        "id": "icar_pop_potato_healthy_gap",
        "crop": "Potato",
        "disease": "Healthy Crop",
        "pest": "Routine Scouting",
        "authority": "ICAR-Central Potato Research Institute (CPRI), Shimla",
        "document_title": "Good Agricultural Practices (GAP) for High-Yield Seed & Table Potato",
        "page_number": 14,
        "condition_summary": "Lush, dark-green potato canopy, vigorous tuber bulking, absence of foliar blight lesions, and zero vector transmission.",
        "pesticide": {
            "active_ingredient": "Trichoderma harzianum 2% WP (Bio-fungicide Prophylactic)",
            "chemical_name": "Eco-Derma / Bio-Harz",
            "exact_dose_per_liter": "5.0 g/L",
            "withholding_period_days": 0,
            "application_method": "Prophylactic foliar spray before canopy closure. Zero chemical synthetic fungicides needed.",
            "safety_warnings": [
                "Apply bio-agents during overcast sky or evening hours."
            ]
        },
        "fertilizer": {
            "n_ratio": "Standard N-P-K (150:100:120 kg/ha split)",
            "p_ratio": "SSP 100 kg/ha basal",
            "k_ratio": "MOP/SOP 120 kg/ha in 2 splits",
            "micronutrients": ["Zinc Sulphate 0.5%", "Boron 0.1% foliar"],
            "instructions": "Earthing up with balanced potassium fertilization at 30-35 DAP to promote tuber enlargement and thicken tuber skin."
        },
        "ipm": {
            "cultural": [
                "Earthing-up to provide at least 10 cm protective soil cover over forming tubers.",
                "Maintain furrow irrigation without inundating ridge tops."
            ],
            "biological": [
                "Tuber seed treatment with Trichoderma viride @ 5 g/kg seed tuber before planting."
            ],
            "mechanical": [
                "Yellow sticky traps @ 15 traps/acre for aphid vector monitoring."
            ],
            "chemical": [
                "Zero chemical pesticides required for healthy crops. Continue scouting."
            ]
        },
        "monitoring": {
            "day_1": "Inspect ridges for proper soil coverage over developing tubers.",
            "day_3": "Check yellow water pan/sticky traps for winged aphid vectors.",
            "day_7": "Examine lower leaves inside dense canopy for humidity symptoms.",
            "day_14": "Sample 3 hills to monitor tuber sizing and uniform stolon bulking."
        }
    },
    {
        "id": "icar_pop_pepper_bacterial_spot",
        "crop": "Pepper",
        "disease": "Bacterial Spot",
        "pest": "Thrips",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Guidelines for Bacterial Spot & Canker Control in Capsicum and Chilli",
        "page_number": 29,
        "condition_summary": "Xanthomonas campestris pv. vesicatoria small, dark water-soaked spots with yellow chlorotic rings on leaves, causing severe premature defoliation in warm wet conditions.",
        "pesticide": {
            "active_ingredient": "Streptocycline 90:10 + Copper Oxychloride 50% WP",
            "chemical_name": "Streptocycline + Blitox 50 WP",
            "exact_dose_per_liter": "0.1 g/L (Streptocycline) + 2.5 g/L (Blitox)",
            "withholding_period_days": 5,
            "application_method": "High-volume foliar spray ensuring thorough wetting of both leaf surfaces.",
            "safety_warnings": [
                "Do not spray copper formulations during full bloom to prevent flower drop."
            ]
        },
        "fertilizer": {
            "n_ratio": "Moderate Nitrogen (-20%)",
            "p_ratio": "Standard Phosphorus (50 kg/ha)",
            "k_ratio": "Potassium Schoenite @ 5 g/L foliar",
            "micronutrients": ["Borax 0.1%", "Calcium Nitrate 0.5%"],
            "instructions": "Avoid high urea doses. Apply Calcium Nitrate @ 5 g/L + Boron 0.1% to improve membrane stability against bacterial wall-degrading enzymes."
        },
        "ipm": {
            "cultural": [
                "Hot water seed treatment at 50°C for 25 minutes prior to nursery sowing.",
                "Rogue out and destroy infected pepper seedlings in nursery.",
                "Drip irrigation to avoid leaf wetness duration."
            ],
            "biological": [
                "Seedling root dip in Pseudomonas fluorescens @ 10 g/L.",
                "Foliar spray of Bacillus subtilis @ 5 g/L."
            ],
            "mechanical": [
                "Disinfect harvesting shears and stakes with 1% potassium permanganate solution."
            ],
            "chemical": [
                "Streptocycline @ 0.1 g/L + Copper Oxychloride 50 WP @ 2.5 g/L at 10-12 day intervals."
            ]
        },
        "monitoring": {
            "day_1": "Apply combined bactericide spray across canopy; prune heavily spotted stems.",
            "day_3": "Check spots for drying out and absence of water-soaked margins.",
            "day_7": "Inspect young terminal shoots for clean, unspotted leaves.",
            "day_14": "Check fruit setting on treated plants."
        }
    },
    {
        "id": "icar_pop_pepper_healthy_gap",
        "crop": "Pepper",
        "disease": "Healthy Crop",
        "pest": "Routine Scouting",
        "authority": "ICAR-Indian Institute of Horticultural Research (IIHR), Bengaluru",
        "document_title": "Good Agricultural Practices (GAP) for Bell Pepper & Chilli Cultivation",
        "page_number": 12,
        "condition_summary": "Glossy, dark-green foliage, abundant flower bud formation, absence of leaf curling or spots, and zero thrips infestation.",
        "pesticide": {
            "active_ingredient": "Pseudomonas fluorescens 2% WP + Neem Oil 1500 ppm",
            "chemical_name": "Bio-Shield + Neem Guard",
            "exact_dose_per_liter": "5.0 g/L (Bio-Shield) + 3.0 ml/L (Neem Oil)",
            "withholding_period_days": 0,
            "application_method": "Prophylactic canopy spray in early morning. Zero chemical pesticides required.",
            "safety_warnings": [
                "Do not mix chemical bactericides with beneficial bio-agents."
            ]
        },
        "fertilizer": {
            "n_ratio": "Standard N-P-K (120:60:80 kg/ha)",
            "p_ratio": "Single Super Phosphate 60 kg/ha basal",
            "k_ratio": "Potassium Nitrate (13:0:45) @ 5 g/L foliar at flowering",
            "micronutrients": ["Zinc Sulphate 0.5%", "Boron 0.1%"],
            "instructions": "Apply balanced water-soluble fertigation (19:19:19 @ 3 g/L) + micronutrient foliar spray (Zn, B) to prevent flower drop and promote pod expansion."
        },
        "ipm": {
            "cultural": [
                "Maintain 45 x 45 cm spacing with silver-black reflective mulch.",
                "Keep bunds free of weed hosts."
            ],
            "biological": [
                "Prophylactic Trichoderma viride application to root zone via drip irrigation."
            ],
            "mechanical": [
                "Install blue sticky traps @ 15 traps/acre (for thrips) and yellow sticky traps (for aphids/whiteflies)."
            ],
            "chemical": [
                "Zero chemical pesticides required for healthy crops. Continue scouting."
            ]
        },
        "monitoring": {
            "day_1": "Inspect canopy for uniform growth and shiny leaf texture.",
            "day_3": "Check blue and yellow sticky traps for vector counts.",
            "day_7": "Examine flower buds for normal opening without curling.",
            "day_14": "Assess developing pepper pods for size and uniformity."
        }
    }
]
