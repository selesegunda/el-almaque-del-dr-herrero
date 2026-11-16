import json
import tempfile
import unittest
from pathlib import Path
from almaque.collect import topic_for, normalize_doi, classify_official, allowed_host, pubmed_query
from almaque.store import merge
from almaque.render import render


class CoreTests(unittest.TestCase):
    def test_topic_and_classify(self):
        self.assertIn('Páncreas', topic_for('pancreatic adenocarcinoma'))
        self.assertEqual(classify_official('New colorectal cancer clinical guidelines'), 'Guías y protocolos')
        self.assertEqual(normalize_doi('https://doi.org/10.1000/ABC'), '10.1000/abc')

    def test_endocrine_and_asco_coverage(self):
        self.assertIn('Neuroendocrinos', topic_for('pancreatic neuroendocrine tumor'))
        self.assertIn('Neoplasias endocrinas', topic_for('medullary thyroid carcinoma'))
        self.assertIn('Neoplasias endocrinas', topic_for('adrenocortical carcinoma'))
        self.assertIn('Neoplasias endocrinas', topic_for('pheochromocytoma'))
        self.assertIn('Neuroendocrinos', topic_for('pituitary neuroendocrine tumor'))
        self.assertIn('Neoplasias endocrinas', topic_for('pituitary neuroendocrine tumor'))
        self.assertTrue(allowed_host('https://ascopubs.org/doi/10.1200/example'))
        self.assertTrue(allowed_host('https://meetings.asco.org/abstracts-presentations/123'))
        self.assertFalse(allowed_host('https://not-asco.org/example'))
        self.assertIn('"medullary thyroid"[Title/Abstract]', pubmed_query())
        self.assertEqual(classify_official('Neuroendocrine/carcinoid meeting abstract'), 'Comunicaciones científicas')

    def test_dedup_and_versions_and_site(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            db, runs = p/'data/records.json', p/'data/runs.json'
            record={'key':'pmid:123','title':'Example','category':'Artículos científicos','source':'J Clin Oncol','date':'2026','url':'https://pubmed.ncbi.nlm.nih.gov/123/','topics':['Páncreas']}
            _, _, a = merge([record],[],['PubMed'], '2026-11-17T08:00:00+01:00',db,runs)
            self.assertEqual((a['new'],a['updated']),(1,0))
            _, _, b = merge([record],[],['PubMed'], '2026-11-18T08:00:00+01:00',db,runs)
            self.assertEqual((b['new'],b['updated']),(0,0))
            _, _, c = merge([{**record,'title':'Example corrected'}],[],['PubMed'],'2026-11-19T08:00:00+01:00',db,runs)
            self.assertEqual((c['new'],c['updated']),(0,1))
            self.assertEqual(len(json.loads(db.read_text())['pmid:123']['versions']),1)
            render(p/'docs',db,runs)
            self.assertTrue((p/'docs/index.html').exists())
            self.assertEqual(len(json.loads((p/'docs/runs.json').read_text())),3)


if __name__ == '__main__':
    unittest.main()
