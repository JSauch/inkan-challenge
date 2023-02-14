from typing import Union

from django.db import models, IntegrityError
from polymorphic.models import PolymorphicModel

from wargame.exceptions import UnitCannotAttackException, InvalidAttackTargetException, WargameException


# Create your models here.
class Army(models.Model):
    """
    Army model class.
    """
    army = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, default=None,
                             related_name='parent_army')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.army and (self.army_id == self.id):
            raise ValueError("An army cannot have itself as a unit.")
        super().save(force_insert, force_update, using, update_fields)

    def add_unit(self, unit: Union['Unit', 'Army']):
        """
        Adds a new unit to the army instance
        :param unit: the unit to be added to the army, can be a unit instance or another army instance.
        :return: returns the number of units that the army has.
        """
        unit.army = self
        unit.save()
        return self.units.count()

    def remove_unit(self, unit: Union['Unit', 'Army']):
        if self.units.filter(id=unit.id).exists():
            unit.army = None
            unit.save()
            return self.units.count(),
        raise WargameException("Selected unit does not belong to the army.")

    def attack_unit(self, target: 'Unit') -> int:
        """
        Attacks the target unit using the damage value plus any damage modifier that should apply.
        :param target: Target unit that receives the attack .
        :return: Remaining hit points on the unit after the attack.
        :raise InvalidAttackTargetException if the selected target is not a valid target, in this case a unit instance.
        """
        if isinstance(target, Unit):
            total_damage = 0
            for unit in self.units.all():
                try:
                    total_damage += unit.attack_unit(target)
                except UnitCannotAttackException as error:
                    print(error)  # This error should be logged
            return total_damage
        raise InvalidAttackTargetException("The selected target cannot be attacked, "
                                           "select another target, (insert Skyrim arrow joke here...)")


class Unit(PolymorphicModel):
    """
    Base model class for all the units in the wargame, all units should extend from this class.
    """

    BASE_HIT_POINTS = 0
    BASE_ATTACK_DAMAGE = 0

    army = models.ForeignKey(Army, null=True, blank=True, on_delete=models.SET_NULL, default=None, related_name='units')
    hit_points = models.PositiveIntegerField(default=BASE_HIT_POINTS)
    attack_damage = models.PositiveIntegerField(default=BASE_ATTACK_DAMAGE)

    def __init__(self, *args, **kwargs):
        if not args:  # when reading from the database ORM sends the fields as args, if not checked will raise an error.
            kwargs['hit_points'] = kwargs.get('hit_points', self.BASE_HIT_POINTS)
            kwargs['attack_damage'] = kwargs.get('attack_damage', self.BASE_ATTACK_DAMAGE)
        super().__init__(*args, **kwargs)

    @property
    def alive(self) -> bool:
        """
        Returns if a unit is alive or not, a unit is alive if its hit_points are greater than 0
        :return: true if hit points are greater than 0, false otherwise
        """
        return self.hit_points > 0

    @property
    def damage(self):
        """
        Returns the damage a unit can do
        :return: damage the unit does
        """
        return self.attack_damage

    def attack_unit(self, unit: 'Unit') -> int:
        """
        Attacks the target unit using the damage value plus any damage modifier that should apply.
        :param unit: Target unit that receives the attack .
        :return: Remaining hit points on the unit after the attack..
        :raise UnitCannotAttackException if the unit is ded cannot attack
        :raise InvalidAttackTargetException if the selected target is not a valid target, is not a unit instance.
        """
        if isinstance(unit, Unit):
            if self.alive:
                return unit.calculate_incoming_damage(self.damage)
            else:
                raise UnitCannotAttackException("Unit is ded, Rodrigo Díaz de Vivar would be proud though...")
        raise InvalidAttackTargetException("The selected target cannot be attacked, "
                                           "select another target, (insert Skyrim arrow joke here...)")

    def calculate_incoming_damage(self, damage: int) -> int:
        """
        Subtracts the damage received by an incoming unit attack from the unit hit points to a minimum of 0 (RIP unit),
        any damage savings over the incoming attack should be applied here.
        :param damage: incoming damage from the attacking unit
        :return: damage dealt to the unit.
        """
        remaining_hp = self.hit_points - damage
        self.hit_points = max(remaining_hp, 0)  # Gotta one line the hell out of everything, prevents negative hp
        self.save()
        return damage


class Weapon(models.Model):
    """
    Weapon model class.
    """
    damage_value = models.PositiveIntegerField(default=0, null=False, blank=False)
    unit = models.OneToOneField(Unit, null=True, blank=True, on_delete=models.SET_NULL)


class EquipableUnit(Unit):
    """
    Abstract model class extends Unit model, unit models that extend this class will be able to equip weapons.
    Damage calculations will take weapon damage into account if a weapon is equipped.
    """

    def equip_weapon(self, weapon: Weapon) -> (bool, str):
        """
        Equips the selected weapon into a unit if both the weapon and the unit are free.
        :param  weapon instance that will be equipped to the unit
        :return: boolean indicating if the weapon has been equipped and a message with information
        :raise TypeError
        """
        if not isinstance(weapon, Weapon):
            raise TypeError("Parameter 'weapon' must be of type Weapon")

        if weapon.unit:
            return False, "Weapon belongs to another unit."
        elif hasattr(self, "weapon"):
            return False, "Unit is already equipped, remove the current weapon first."
        weapon.unit = self
        weapon.save()
        return True, "Weapon equipped."

    def unequip_weapon(self) -> (bool, str):
        """
        Removes the equipped weapon and makes it available to other "equippable" units.
        :return: boolean indicating if the weapon has been removed, message explaining the output
        """
        if hasattr(self, 'weapon'):
            self.weapon = None
            self.save()
            return True, "Weapon removed."
        else:
            return False, "Unit is not equipped with a weapon."

    @property
    def damage(self) -> int:
        """
        Returns the damage an "equippable" unit can do, if its equipped adds the weapon damage to the base damage.
        :return: the damage base of the unit plus the equipped weapon damage if the unit has one
        """
        attack_damage = self.attack_damage
        if hasattr(self, 'weapon'):
            attack_damage += self.weapon.damage_value
        return attack_damage

    class Meta:
        abstract = True


class Knight(EquipableUnit):

    BASE_ATTACK_DAMAGE = 20
    BASE_HIT_POINTS = 100


class Archer(EquipableUnit):

    BASE_ATTACK_DAMAGE = 25
    BASE_HIT_POINTS = 50


class Catapult(Unit):

    BASE_HIT_POINTS = 200
    BASE_ATTACK_DAMAGE = 50

