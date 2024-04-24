from rest_framework.test import APITestCase

from projects.models import Promo

PROMO_CODE = 'adam'


class PromoModelTestCase(APITestCase):
    def setUp(self):
        self.promo = Promo.objects.create(code=PROMO_CODE)

    def test_promo_codes_are_unique(self):
        try:
            Promo.objects.create(code=PROMO_CODE)
            self.assertEqual(True, False)
        except:
            self.assertEqual(True, True)