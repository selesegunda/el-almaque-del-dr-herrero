"""Transparent editable selection rules, not medical interpretation."""
from __future__ import annotations

CATEGORIES = ["Guías y protocolos", "Artículos científicos", "Comunicaciones científicas", "Noticias"]
TOPICS = {
    "Colorrectal": ["colorectal", "colon cancer", "rectal cancer", "rectal neoplasm", "colon neoplasm"],
    "Gástrico y unión gastroesofágica": ["gastric", "stomach cancer", "gastroesophageal", "gastro-oesophageal"],
    "Esófago": ["esophageal", "oesophageal", "esophagus cancer", "oesophagus cancer"],
    "Páncreas": ["pancreatic cancer", "pancreatic adenocarcinoma", "pancreas neoplasm"],
    "Vías biliares": ["cholangiocarcinoma", "biliary tract", "gallbladder cancer", "bile duct cancer"],
    "Hepatocarcinoma": ["hepatocellular carcinoma", "hepatoma", "liver cancer"],
    "Neuroendocrinos": [
        "neuroendocrine tumor", "neuroendocrine tumour", "neuroendocrine neoplasm",
        "neuroendocrine carcinoma", "neuroendocrine cancer",
        "gastroenteropancreatic neuroendocrine", "pancreatic neuroendocrine",
        "carcinoid tumor", "carcinoid tumour", "carcinoid syndrome",
        "small intestinal neuroendocrine", "large cell neuroendocrine",
        "well-differentiated neuroendocrine", "poorly differentiated neuroendocrine",
        "neuroendocrine/carcinoid", "pituitary neuroendocrine tumor",
    ],
    "Neoplasias endocrinas": [
        "thyroid carcinoma", "thyroid cancer", "thyroid malignancy",
        "thyroid neoplasm", "medullary thyroid", "anaplastic thyroid",
        "adrenocortical carcinoma", "adrenal cortical carcinoma",
        "adrenocortical cancer", "adrenal malignancy", "adrenal cancer",
        "pheochromocytoma", "phaeochromocytoma", "paraganglioma",
        "pituitary carcinoma", "pituitary neuroendocrine tumor",
        "parathyroid carcinoma", "multiple endocrine neoplasia",
    ],
    "Canal anal": ["anal cancer", "anal squamous", "anus neoplasm"],
}
SOCIETIES = ("SEOM", "SAOM", "ESMO", "ASCO")
# Allowlisted journal names; PubMed filters can be extended in this one file.
JOURNALS = [
    "N Engl J Med", "Lancet", "Lancet Oncol", "JAMA", "JAMA Oncol",
    "J Clin Oncol", "Ann Oncol", "ESMO Open", "Clin Transl Oncol", "Nat Med",
    "Gut", "Gastroenterology", "Clin Gastroenterol Hepatol",
    "Cancer Discov", "J Natl Cancer Inst", "Eur J Cancer", "Cancer",
    "JCO Oncol Pract", "JCO Precis Oncol", "Endocr Relat Cancer",
    "Thyroid", "J Clin Endocrinol Metab", "Neuroendocrinology",
]
# Pages used as a lightweight extra source of official links. Site layouts may change.
OFFICIAL_PAGES = {
    "SEOM": ["https://seom.org/publicaciones/guias-clinicas/105418-guias-clinicas-seom"],
    "SAOM": ["https://www.saom.es/"],
    "ESMO": ["https://www.esmo.org/guidelines/guidelines-news", "https://www.esmo.org/meeting-calendar"],
    "ASCO": [
        "https://www.asco.org/gastrointestinal-cancer-guidelines",
        "https://www.asco.org/gi/program/abstracts-posters",
    ],
}
OFFICIAL_HOSTS = {"seom.org", "www.seom.org", "saom.es", "www.saom.es", "esmo.org", "www.esmo.org", "asco.org", "www.asco.org", "ascopubs.org", "www.ascopubs.org", "meetings.asco.org"}
GUIDE_WORDS = ("guideline", "guidelines", "clinical practice", "consensus", "recommendation", "guía", "guías", "protocolo", "actualización", "update")
COMMUNICATION_WORDS = ("abstract", "poster", "póster", "oral presentation", "congress", "congreso", "meeting")
NEWS_WORDS = ("news", "noticia", "press", "comunicado")