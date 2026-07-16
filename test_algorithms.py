import unittest
from core.biology import calculate_biology_and_finance

class TestDecisionEngine(unittest.TestCase):
    
    def setUp(self):
        # Base realistic settings for a 35-day-old broiler flock
        self.base_kwargs = {
            'fan_count': 10,
            'fan_capacity': 40000.0,
            'width': 16.0,
            'ridge_h': 4.5,
            'eaves_h': 2.5,
            'bird_count': 30000,
            'bird_weight': 2.2,
            'bird_age': 35,
            'kwh_consumed': 100.0,
            'feed_price': 15.0,
            'meat_price': 60.0,
            'electricity_price': 3.5,
            'delta_t': 0.0,
            'worst_nh3_zone': "zone-1",
            't_out': 20.0
        }

    def test_optimum_conditions(self):
        # Target temp for 35 days: max(20.0, 33.0 - (35 * 0.35)) = max(20, 33 - 12.25) = 20.75
        # If t_eff is around 20.75, it's optimum.
        kwargs = self.base_kwargs.copy()
        t_in_array = [20.75, 20.75, 20.75]
        nh3_array = [10.0, 10.0, 10.0]
        co2_array = [800.0, 800.0, 800.0]
        
        # At 0 fan capacity, t_eff == t_in
        kwargs['fan_capacity'] = 0.0
        
        result = calculate_biology_and_finance(t_in_array, [], nh3_array, co2_array, **kwargs)
        
        actions = result['actions']
        titles = [a['title'] for a in actions]
        
        self.assertIn("Optimum Koşullar", titles)
        self.assertEqual(result['fcr_penalty'], 0.0)

    def test_cold_shock_rule(self):
        kwargs = self.base_kwargs.copy()
        # Internal temp is 25, external is 5.
        t_in_array = [25.0, 25.0, 25.0]
        nh3_array = [10.0, 10.0, 10.0]
        co2_array = [800.0, 800.0, 800.0]
        
        kwargs['t_out'] = 5.0
        kwargs['fan_capacity'] = 40000.0 # Fans are running
        
        result = calculate_biology_and_finance(t_in_array, [], nh3_array, co2_array, **kwargs)
        
        titles = [a['title'] for a in result['actions']]
        self.assertIn("Aşırı Isıtma Maliyeti & Termal Şok", titles)

    def test_ammonia_poisoning(self):
        kwargs = self.base_kwargs.copy()
        t_in_array = [20.75, 20.75, 20.75]
        nh3_array = [10.0, 30.0, 10.0] # 30 is > 25 limit
        co2_array = [800.0, 800.0, 800.0]
        kwargs['fan_capacity'] = 0.0
        
        result = calculate_biology_and_finance(t_in_array, [], nh3_array, co2_array, **kwargs)
        
        titles = [a['title'] for a in result['actions']]
        self.assertIn("Amonyak Zehirlenmesi", titles)

    def test_high_temperature_stress(self):
        kwargs = self.base_kwargs.copy()
        # Target is 20.75. Let's make t_eff = 26.0
        t_in_array = [26.0, 26.0, 26.0]
        nh3_array = [10.0, 10.0, 10.0]
        co2_array = [800.0, 800.0, 800.0]
        kwargs['fan_capacity'] = 0.0
        
        result = calculate_biology_and_finance(t_in_array, [], nh3_array, co2_array, **kwargs)
        
        titles = [a['title'] for a in result['actions']]
        self.assertIn("Yüksek Sıcaklık Stresi", titles)
        # Should also trigger FCR penalty because t > 25.0
        self.assertGreater(result['fcr_penalty'], 0.0)
        self.assertIn("Yem İsrafı Alarmı", titles)

    def test_mortality_risk_due_to_co2(self):
        kwargs = self.base_kwargs.copy()
        t_in_array = [20.75, 20.75, 20.75]
        nh3_array = [10.0, 10.0, 10.0]
        co2_array = [10000.0, 10000.0, 10000.0] # > 3000 limit, enough to break 0.001 mortality rate
        kwargs['fan_capacity'] = 0.0
        
        result = calculate_biology_and_finance(t_in_array, [], nh3_array, co2_array, **kwargs)
        
        titles = [a['title'] for a in result['actions']]
        self.assertIn("Kritik Ölüm Riski", titles)
        self.assertGreater(result['dead_birds'], 0)

if __name__ == '__main__':
    unittest.main()
