from django.test import TestCase

from wargame import models
from wargame.exceptions import InvalidAttackTargetException, WargameException, UnitCannotAttackException


# Create your tests here.
class WargameTestCase(TestCase):

    def setUp(self) -> None:

        # Create some units and armies for our tests.
        self.knight_1 = models.Knight.objects.create()
        self.knight_2 = models.Knight.objects.create()
        self.equipped_knight = models.Knight.objects.create()
        self.dead_knight = models.Knight.objects.create(hit_points=0)

        self.archer_1 = models.Archer.objects.create()
        self.archer_2 = models.Archer.objects.create()
        self.equipped_archer = models.Archer.objects.create()
        self.dead_archer = models.Archer.objects.create(hit_points=0)

        self.catapult_1 = models.Catapult.objects.create()
        self.catapult_2 = models.Catapult.objects.create()
        self.destroyed_catapult = models.Catapult.objects.create(hit_points=0)

        self.army_1 = models.Army.objects.create()
        self.army_2 = models.Army.objects.create()
        self.empty_army = models.Army.objects.create()

        self.sword = models.Weapon.objects.create(damage_value=10)
        self.longbow = models.Weapon.objects.create(damage_value=5)
        self.longsword = models.Weapon.objects.create(damage_value=20)
        self.recurve_bow = models.Weapon.objects.create(damage_value=15)


        # Set foreign keys manually.
        self.equipped_knight.weapon = self.sword
        self.equipped_archer.weapon = self.longbow
        self.equipped_knight.save()
        self.equipped_archer.save()

        army_1_list = [self.knight_1, self.archer_1, self.catapult_1]
        army_2_list = [self.knight_2, self.archer_2, self.catapult_2]

        for unit in army_1_list:
            unit.army = self.army_1
            unit.save()
        for unit in army_2_list:
            unit.army = self.army_2
            unit.save()

    def test_army_add_unit(self):
        past_number_of_units = self.army_2.units.count()
        self.army_2.add_unit(self.knight_1)
        self.assertEqual(self.army_2.units.count(), past_number_of_units+1)

    def test_army_add_owned_unit(self):
        past_number_of_units = self.army_2.units.count()
        self.army_2.add_unit(self.knight_2)
        self.assertEqual(self.army_2.units.count(), past_number_of_units)

    def test_army_remove_unit(self):
        past_number_of_units = self.army_2.units.count()
        self.army_2.remove_unit(self.knight_2)
        self.assertEqual(self.army_2.units.count(), past_number_of_units-1)

    def test_army_remove_not_owned_unit(self):
        number_of_units = self.army_2.units.count()
        with self.assertRaises(WargameException):
            self.army_2.remove_unit(self.knight_1)
        self.assertEqual(number_of_units, self.army_2.units.count())

    def test_unit_only_exists_in_one_army(self):
        previous_army = self.archer_2.army
        self.army_1.add_unit(self.archer_2)
        current_army = self.archer_2.army
        self.assertNotEqual(previous_army.id, self.archer_2.army.id)
        self.assertEqual(current_army.id, self.archer_2.army.id)

    def test_army_attack_army(self):
        with self.assertRaises(InvalidAttackTargetException):
            self.army_1.attack_unit(self.army_2)

    def test_army_attack_unit(self):
        damage_dealt = self.army_1.attack_unit(self.catapult_1)
        expected_damage = sum(unit.damage for unit in self.army_1.units.all())
        self.assertEqual(damage_dealt, expected_damage)

    def test_unit_attack_army(self):
        with self.assertRaises(InvalidAttackTargetException):
            self.knight_1.attack_unit(self.army_2)

    def test_unit_attack_unit(self):
        damage_dealt = self.knight_1.attack_unit(self.archer_2)
        self.assertEqual(damage_dealt, self.knight_1.damage)

    def test_unit_attack_unit_attacker_is_dead(self):
        with self.assertRaises(UnitCannotAttackException):
            damage = self.dead_archer.attack_unit(self.dead_knight)
            self.assertIsNone(damage)

    def test_equipped_unit_adds_weapon_damage(self):
        damage_dealt = self.equipped_knight.attack_unit(self.archer_1)
        self.assertEqual(damage_dealt, self.equipped_knight.attack_damage + self.equipped_knight.weapon.damage_value)

    def test_equip_weapon(self):
        print(self.recurve_bow.unit)
        result, msg = self.archer_2.equip_weapon(self.recurve_bow)
        self.assertTrue(result)
        self.assertEqual(msg, 'Weapon equipped.')

    def test_weapon_can_be_removed(self):
        self.equipped_archer.unequip_weapon()
        self.assertIsNone(self.longbow.unit)
        self.equipped_archer.equip_weapon(self.longbow)

    def test_equip_weapon_already_equipped(self):
        result, msg = self.knight_1.equip_weapon(self.sword)
        self.assertFalse(result)
        self.assertEqual(msg, 'Weapon belongs to another unit.')

    def test_equip_weapon_to_equipped_unit(self):
        result, msg = self.equipped_knight.equip_weapon(self.longsword)
        self.assertFalse(result)
        self.assertEqual(msg, 'Unit is already equipped, remove the current weapon first.')

    def test_equip_weapon_not_a_weapon(self):
        with self.assertRaises(TypeError):
            self.equipped_archer.equip_weapon(self.catapult_1)

    def test_equip_weapon_unequippable_unit(self):
        with self.assertRaises(AttributeError):
            self.catapult_1.equip_weapon(self.longsword)




