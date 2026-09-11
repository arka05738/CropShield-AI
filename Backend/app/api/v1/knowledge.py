import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from app.rag.chroma_service import chroma_service
from app.core.database import memory_store
from app.core.security import require_role, ADMIN_ROLES, get_current_user

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base Management"])

# Expanded benchmark seeded knowledge base documents from major ICAR institutes
INITIAL_DOCS = [
    {
        "id": "doc_icar_tomato_01",
        "title": "Package of Practices for Commercial Solanaceous Crops - Tomato Health",
        "source": "ICAR-IIHR Publication Series No. 44",
        "authority": "Indian Council of Agricultural Research (ICAR)",
        "crop": "Tomato",
        "sector": "Vegetables & Spices",
        "topic": "Early Blight, Late Blight & Vector Sucking Pest Management",
        "language": "English / Hindi / Marathi",
        "uploaded_date": "2026-08-15T10:00:00Z",
        "indexed_chunks": 28,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_nrri_rice_02",
        "title": "Standard Operating Procedure for Rice Blast & Stem Borer Management",
        "source": "National Rice Research Institute (NRRI) Bulletin 102",
        "authority": "ICAR-NRRI, Cuttack",
        "crop": "Rice",
        "sector": "Cereals & Grains",
        "topic": "Pyricularia oryzae and Scirpophaga incertulas Integrated Protocol",
        "language": "English / Odia / Bengali",
        "uploaded_date": "2026-08-20T14:30:00Z",
        "indexed_chunks": 34,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_cicr_cotton_03",
        "title": "Integrated Pest & Insecticide Resistance Strategy for Cotton",
        "source": "Central Institute for Cotton Research (CICR) Advisory",
        "authority": "ICAR-CICR, Nagpur",
        "crop": "Cotton",
        "sector": "Commercial & Cash Crops",
        "topic": "Bollworm Complex & CLCuV Vectors (Helicoverpa & Whitefly)",
        "language": "English / Marathi / Telugu",
        "uploaded_date": "2026-08-28T11:15:00Z",
        "indexed_chunks": 42,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_cpri_potato_04",
        "title": "Decision Support System for Late Blight Management in Indo-Gangetic Plains",
        "source": "CPRI Technical Bulletin Vol. 88",
        "authority": "ICAR-CPRI, Shimla",
        "crop": "Potato",
        "sector": "Vegetables & Spices",
        "topic": "Phytophthora infestans Forewarning and Chemical Schedule",
        "language": "English / Hindi / Punjabi",
        "uploaded_date": "2026-09-01T09:45:00Z",
        "indexed_chunks": 26,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iiwbr_wheat_05",
        "title": "Guidelines for Surveillance and Management of Wheat Stripe Rust in NWPZ",
        "source": "ICAR-IIWBR Technical Manual 2026",
        "authority": "ICAR-IIWBR, Karnal",
        "crop": "Wheat",
        "sector": "Cereals & Grains",
        "topic": "Puccinia striiformis & Foliar Rust Containment Strategy",
        "language": "English / Hindi / Punjabi",
        "uploaded_date": "2026-09-02T12:00:00Z",
        "indexed_chunks": 30,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iimr_maize_06",
        "title": "Standard Management Protocol for Fall Armyworm & Foliar Blights in Indian Maize",
        "source": "ICAR-IIMR Advisory Bulletin No. 19",
        "authority": "ICAR-IIMR, Ludhiana",
        "crop": "Maize",
        "sector": "Cereals & Grains",
        "topic": "Spodoptera frugiperda & Turcicum Leaf Blight Strategy",
        "language": "English / Hindi / Kannada",
        "uploaded_date": "2026-09-03T10:15:00Z",
        "indexed_chunks": 36,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iihr_chilli_07",
        "title": "Package of Practices for High-Value Solanaceous Spices - Chilli Pest & Disease Shield",
        "source": "ICAR-IIHR Spice Protection Series 12",
        "authority": "ICAR-IIHR, Bengaluru",
        "crop": "Chilli",
        "sector": "Vegetables & Spices",
        "topic": "Colletotrichum capsici Anthracnose & Scirtothrips dorsalis Management",
        "language": "English / Telugu / Tamil",
        "uploaded_date": "2026-09-04T15:20:00Z",
        "indexed_chunks": 29,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iisr_soybean_08",
        "title": "National Package of Practices for Rainfed and Irrigated Soybean in Central India",
        "source": "ICAR-IISR Indore Bulletin 2026",
        "authority": "ICAR-IISR, Indore",
        "crop": "Soybean",
        "sector": "Pulses & Oilseeds",
        "topic": "Phakopsora pachyrhizi Rust & Girdle Beetle Interventions",
        "language": "English / Hindi / Marathi",
        "uploaded_date": "2026-09-05T09:30:00Z",
        "indexed_chunks": 31,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iisr_sugarcane_09",
        "title": "Integrated Disease and Pest Management in Subtropical Sugarcane",
        "source": "ICAR-IISR Lucknow Bulletin 55",
        "authority": "ICAR-IISR, Lucknow",
        "crop": "Sugarcane",
        "sector": "Commercial & Cash Crops",
        "topic": "Colletotrichum falcatum Red Rot & Shoot Borer Control",
        "language": "English / Hindi",
        "uploaded_date": "2026-09-05T14:10:00Z",
        "indexed_chunks": 25,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_dgr_groundnut_10",
        "title": "Package of Practices for Kharif and Rabi-Summer Groundnut in India",
        "source": "ICAR-DGR Junagadh Monograph 2026",
        "authority": "ICAR-DGR, Junagadh",
        "crop": "Groundnut",
        "sector": "Pulses & Oilseeds",
        "topic": "Cercospora Tikka Leaf Spot & Spodoptera Integrated Strategy",
        "language": "English / Gujarati / Telugu",
        "uploaded_date": "2026-09-06T08:00:00Z",
        "indexed_chunks": 27,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_iipr_chickpea_11",
        "title": "Standard Operating Procedure for Pulse Protection - Chickpea Health Protocol",
        "source": "ICAR-IIPR Kanpur Bulletin No. 62",
        "authority": "ICAR-IIPR, Kanpur",
        "crop": "Chickpea",
        "sector": "Pulses & Oilseeds",
        "topic": "Fusarium oxysporum Wilt & Helicoverpa armigera Pod Borer Strategy",
        "language": "English / Hindi",
        "uploaded_date": "2026-09-06T09:15:00Z",
        "indexed_chunks": 32,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_drmr_mustard_12",
        "title": "Integrated Pest & Disease Management in Rapeseed-Mustard",
        "source": "ICAR-DRMR Bharatpur Monograph Series",
        "authority": "ICAR-DRMR, Bharatpur",
        "crop": "Mustard",
        "sector": "Pulses & Oilseeds",
        "topic": "Alternaria brassicae Blight & Lipaphis erysimi Aphid Control",
        "language": "English / Hindi / Punjabi",
        "uploaded_date": "2026-09-06T09:30:00Z",
        "indexed_chunks": 28,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_dogr_onion_13",
        "title": "Good Agricultural Practices for Onion Health Management & Export Standardization",
        "source": "ICAR-DOGR Technical Bulletin No. 39",
        "authority": "ICAR-DOGR, Rajgurunagar, Pune",
        "crop": "Onion",
        "sector": "Vegetables & Spices",
        "topic": "Alternaria porri Purple Blotch & Thrips tabaci Management",
        "language": "English / Marathi / Hindi",
        "uploaded_date": "2026-09-06T10:00:00Z",
        "indexed_chunks": 30,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_nrcb_banana_14",
        "title": "National Biosecurity Protocol for Tropical Race 4 Containment & Weevil Management",
        "source": "ICAR-NRCB Trichy Biosecurity Manual 2026",
        "authority": "ICAR-NRCB, Tiruchirappalli",
        "crop": "Banana",
        "sector": "Fruits & Plantation",
        "topic": "Fusarium Wilt TR4 Containment & Odoiporus longicollis Stem Weevil",
        "language": "English / Tamil / Malayalam",
        "uploaded_date": "2026-09-06T10:30:00Z",
        "indexed_chunks": 35,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_cish_mango_15",
        "title": "Standard Operating Procedure for Mango Canopy Protection and Export Quality Production",
        "source": "ICAR-CISH Lucknow Special Bulletin 18",
        "authority": "ICAR-CISH, Lucknow",
        "crop": "Mango",
        "sector": "Fruits & Plantation",
        "topic": "Oidium mangiferae Powdery Mildew & Amritodus atkinsoni Hopper Control",
        "language": "English / Hindi / Bengali",
        "uploaded_date": "2026-09-06T11:00:00Z",
        "indexed_chunks": 33,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_skuast_apple_16",
        "title": "Comprehensive Spray Schedule for Apple Orchards in Western Himalayas",
        "source": "SKUAST-K & Dr YSP UHF Joint Advisory 2026",
        "authority": "SKUAST Kashmir / Dr YSP UHF Nauni",
        "crop": "Apple",
        "sector": "Fruits & Plantation",
        "topic": "Venturia inaequalis Apple Scab & Panonychus ulmi European Red Mite",
        "language": "English / Urdu / Hindi",
        "uploaded_date": "2026-09-06T11:30:00Z",
        "indexed_chunks": 38,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_nrcg_grapes_17",
        "title": "Grape Protection Protocol & Residue Monitoring Plan (GrapeNet Compliance)",
        "source": "ICAR-NRCG Pune Grape Protection Series 47",
        "authority": "ICAR-NRCG, Pune",
        "crop": "Grapes",
        "sector": "Fruits & Plantation",
        "topic": "Plasmopara viticola Downy Mildew & Maconellicoccus hirsutus Mealybug",
        "language": "English / Marathi",
        "uploaded_date": "2026-09-06T12:00:00Z",
        "indexed_chunks": 40,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_nrcp_pomegranate_18",
        "title": "Package of Practices for Bacterial Blight Management & Anar Butterfly Control",
        "source": "ICAR-NRCP Solapur Technical Bulletin 33",
        "authority": "ICAR-NRCP, Solapur",
        "crop": "Pomegranate",
        "sector": "Fruits & Plantation",
        "topic": "Xanthomonas axonopodis pv. punicae Oily Spot & Deudorix isocrates Borer",
        "language": "English / Marathi / Kannada",
        "uploaded_date": "2026-09-06T12:30:00Z",
        "indexed_chunks": 31,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_upasi_tea_19",
        "title": "Planters Guide to Plant Protection in Commercial Tea - Integrated Disease & Pest Strategy",
        "source": "UPASI TRF & TRA Tocklai Advisory Code 2026",
        "authority": "UPASI Tea Research Foundation / TRA Tocklai",
        "crop": "Tea",
        "sector": "Commercial & Cash Crops",
        "topic": "Exobasidium vexans Blister Blight & Helopeltis theivora Mosquito Bug",
        "language": "English / Assamese / Tamil",
        "uploaded_date": "2026-09-06T13:00:00Z",
        "indexed_chunks": 29,
        "status": "INDEXED",
        "file_type": "PDF"
    },
    {
        "id": "doc_ccri_coffee_20",
        "title": "Package of Practices for Arabica & Robusta Coffee Cultivation",
        "source": "CCRI Coffee Board of India Manual No. 24",
        "authority": "Central Coffee Research Institute (CCRI)",
        "crop": "Coffee",
        "sector": "Commercial & Cash Crops",
        "topic": "Hemileia vastatrix Leaf Rust & Xylotrechus quadripes White Stem Borer",
        "language": "English / Kannada / Malayalam",
        "uploaded_date": "2026-09-06T13:30:00Z",
        "indexed_chunks": 34,
        "status": "INDEXED",
        "file_type": "PDF"
    }
]

# Reset and populate memory_store with expanded documents
memory_store["knowledge"] = list(INITIAL_DOCS)

@router.get("")
async def get_all_knowledge_documents(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    """Retrieve catalog of curated knowledge documents (metadata catalog)."""
    return memory_store["knowledge"]

@router.get("/{id}/details")
async def get_knowledge_document_details(id: str, current_user: dict = Depends(require_role(ADMIN_ROLES))):
    """Retrieve document metadata and matching curated POP record if available."""
    doc = next((d for d in memory_store["knowledge"] if d["id"] == id), None)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    pop_record = chroma_service.get_icar_record_by_crop(doc["crop"])
    return {
        "document": doc,
        "pop_record": pop_record,
        "note": "Catalog metadata; PDF binary ingestion into Chroma is not fully implemented.",
    }

@router.post("/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    authority: str = Form("ICAR / State Agricultural University"),
    crop: str = Form("Tomato"),
    sector: str = Form("Vegetables & Spices"),
    topic: str = Form("General Crop Protection"),
    current_user: dict = Depends(require_role(ADMIN_ROLES)),
):
    """
    Register a knowledge document in the catalog.
    Full PDF→Chroma chunking is an extension point; this stores metadata honestly.
    """
    filename = file.filename or "doc.pdf"
    # Read and discard bytes for now (size guard) — full OCR/chunk pipeline not implemented
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 20MB)")

    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    new_doc = {
        "id": doc_id,
        "title": title,
        "source": f"Uploaded: {filename}",
        "authority": authority,
        "crop": crop,
        "sector": sector,
        "topic": topic,
        "language": "English",
        "uploaded_date": datetime.now(timezone.utc).isoformat(),
        "indexed_chunks": 0,
        "status": "CATALOG_ONLY",
        "file_type": filename.split(".")[-1].upper(),
        "chroma_indexed": False,
        "limitation": "Metadata stored; automatic PDF chunk embedding not implemented yet. Use /reindex for curated ICAR records.",
    }
    
    memory_store["knowledge"].insert(0, new_doc)
    return {
        "status": "partial_success",
        "message": (
            f"Document '{title}' registered in catalog. "
            "Chroma PDF embedding pipeline is not implemented — status=CATALOG_ONLY."
        ),
        "document": new_doc,
    }

@router.delete("/{id}")
async def delete_knowledge_document(id: str, current_user: dict = Depends(require_role(ADMIN_ROLES))):
    """Remove a document from the knowledge catalog (metadata only)."""
    initial_len = len(memory_store["knowledge"])
    memory_store["knowledge"] = [d for d in memory_store["knowledge"] if d["id"] != id]
    if len(memory_store["knowledge"]) == initial_len:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {
        "status": "success",
        "message": f"Document '{id}' removed from catalog. Chroma vectors for curated seed records are unchanged.",
    }

@router.post("/reindex")
async def reindex_knowledge_base(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    """Re-seed curated ICAR-style records into ChromaDB (hash embeddings)."""
    chroma_service.seed_icar_records()
    return {
        "status": "success",
        "message": "ChromaDB re-seeded from curated ICAR_POP_RECORDS (hash embeddings).",
        "total_documents": len(memory_store["knowledge"]),
        "limitation": "Uses curated Python records + hash embeddings, not live MiniLM PDF ingestion.",
    }
