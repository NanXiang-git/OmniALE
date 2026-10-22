import unittest, copy
from grade import aggregate
class DeliveryTests(unittest.TestCase):
 def setUp(self):
  self.t={'consistency_f1':1,'metrics':{'values':dict(pitch_global_f1=1,pitch_time_macro_f1=1,pitch_register_macro_f1=1,rhythm_strict_f1=1),'coarse_tp':100,'predicted_count':100,'reference_count':100,'time_bins':[{'f1':1}]*6,'register_bins':[{'f1':1}]*3}}
  self.r=dict(layout=1,notation=1,fidelity=1,delivery_level='ready')
 def test_perfect(self):self.assertEqual(aggregate(self.t,self.r)['final_score'],100)
 def test_unusable_not_zero(self):
  self.r.update(layout=0,fidelity=0,notation=.5,delivery_level='unusable_or_inconsistent')
  high=aggregate(self.t,self.r)['final_score'];low=copy.deepcopy(self.t);low['metrics']['values']={k:v*.4 for k,v in low['metrics']['values'].items()}
  self.assertGreater(high,aggregate(low,self.r)['final_score']);self.assertLessEqual(high,25)
 def test_accuracy_cap(self):
  self.t['metrics']['coarse_tp']=70;self.assertEqual(aggregate(self.t,self.r)['final_score'],59)
 def test_unknown_is_not_zero(self):
  self.r['layout']=None;self.assertIsNone(aggregate(self.t,self.r)['final_score'])
 def test_bad_midi_cannot_be_waived(self):
  self.t['consistency_f1']=.4;self.assertEqual(aggregate(self.t,self.r)['delivery_factor'],.25)
 def test_missing_delivery_limit(self):
  self.r['delivery_level']='missing_core';self.assertLessEqual(aggregate(self.t,self.r)['final_score'],10)
 def test_empty(self):
  self.r.update(layout=0,notation=0,fidelity=0,delivery_level='empty');self.assertEqual(aggregate({},self.r)['final_score'],0)
if __name__=='__main__':unittest.main()
