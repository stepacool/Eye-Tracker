from random import randrange, choice

# def randomizer():
# 	optional_trait_1 = 0
# 	optional_trait_2 = 0
# 	while optional_trait_1 == optional_trait_2:
# 		optional_trait_1 = randrange(0, 16)
# 		optional_trait_2 = randrange(0, 16)
# 	gifted = 1 if optional_trait_2 == 7 or optional_trait_1 == 7 else 0
# 	points = 33
# 	perks = ['ST', 'PE', 'EN', 'CH', 'IN', 'AG', 'LK']
# 	stats = { 
# 		"ST" : 1,
# 		"PE" : 1,
# 		"EN" : 1,
# 		"CH" : 1,
# 		"IN" : 1,
# 		"AG" : 1,
# 		"LK" : 1,
# 	}
# 	traits = ['Bloody Mess', 'Bruiser', 'Chem Reliant', 'Chem Resistant',
# 	'Fast Metabolism', 'Fast Shot', 'Finesse', 'Gifted', 'Good Natured',
# 	'Heavy Handed', 'Jinxed', 'Kamikaze', 'One Hander', 'Sex Appeal', 'Skilled', 'Small Frame']
# 	skills = ['Small Guns', 'Big Guns ', 'Energy Weapons', 'Unarmed', 'Melee Weapons',
# 	'Throwing ', 'First Aid', 'Doctor', 'Sneak', 'Lockpick', 'Steal', 'Traps', 'Science',
# 	'Repair', 'Speech', 'Barter', 'Gambling', 'Outdoorsman']
# 	skill1 = 0
# 	skill2 = 0
# 	skill3 = 0
# 	while skill1 == skill2 or skill2 == skill3 or skill3 == skill1:
# 		skill1, skill2, skill3 = choice(skills), choice(skills), choice(skills)
# 	if gifted:
# 		for i in stats.keys():
# 			stats[i] += 1
# 	while points > 0:
# 		upper_points = randrange(2,7) if points > 7 else points
# 		points_to_perk = randrange(1, upper_points + 1)
# 		perknum = randrange(0, 7) 
# 		if stats[perks[perknum]] + points_to_perk <= 10:
# 			stats[perks[perknum]] += points_to_perk
# 			points -= points_to_perk
# 	optional_trait_1 = traits[optional_trait_1]
# 	optional_trait_2 = traits[optional_trait_2]
# 	if optional_trait_2 == "Bruiser" or optional_trait_1 == "Bruiser":
# 		stats["ST"] += 2
# 	if optional_trait_1 == "Small Frame" or optional_trait_2 == "Small Frame":
# 		stats["AG"] += 1
# 	print("Stats: ", stats)
# 	print("Optional traits: {}, {}".format(optional_trait_1, optional_trait_2))
# 	print("Skills: {}, {}, {} \n".format(skill3, skill2, skill1),)

# if __name__ == "__main__":
# 	randomizer()


class Generator:

	def __init__(self):
		self.points = 33
		self.perks = ['ST', 'PE', 'EN', 'CH', 'IN', 'AG', 'LK']
		self.traits = ['Bloody Mess', 'Bruiser', 'Chem Reliant', 'Chem Resistant',
	'Fast Metabolism', 'Fast Shot', 'Finesse', 'Gifted', 'Good Natured',
	'Heavy Handed', 'Jinxed', 'Kamikaze', 'One Hander', 'Sex Appeal', 'Skilled', 'Small Frame']
		self.skills = ['Small Guns', 'Big Guns ', 'Energy Weapons', 'Unarmed', 'Melee Weapons',
	'Throwing ', 'First Aid', 'Doctor', 'Sneak', 'Lockpick', 'Steal', 'Traps', 'Science',
	'Repair', 'Speech', 'Barter', 'Gambling', 'Outdoorsman']
		self.stats = { 
		"ST" : 1,
		"PE" : 1,
		"EN" : 1,
		"CH" : 1,
		"IN" : 1,
		"AG" : 1,
		"LK" : 1,
	}

	def gen_traits(self):
		self.optional_trait_1 = 0
		self.optional_trait_2 = 0
		while self.optional_trait_1 == self.optional_trait_2:
			self.optional_trait_1 = randrange(0, 16)
			self.optional_trait_2 = randrange(0, 16)
		self.gifted = 1 if self.optional_trait_2 == 7 or self.optional_trait_1 == 7 else 0
		if self.gifted:
			for i in self.stats.keys():
				self.stats[i] += 1
		self.optional_trait_1 = self.traits[self.optional_trait_1]
		self.optional_trait_2 = self.traits[self.optional_trait_2]
		if self.optional_trait_2 == "Bruiser" or self.optional_trait_1 == "Bruiser":
			self.stats["ST"] += 2
		if self.optional_trait_1 == "Small Frame" or self.optional_trait_2 == "Small Frame":
			self.stats["AG"] += 1

		return self.optional_trait_2, self.optional_trait_1

	def gen_skills(self):
		self.skill1 = 0
		self.skill2 = 0
		self.skill3 = 0
		while self.skill1 == self.skill2 or self.skill2 == self.skill3 or self.skill3 == self.skill1:
			self.skill1, self.skill2, self.skill3 = choice(self.skills), choice(self.skills), choice(self.skills)
		return self.skill1, self.skill2, self.skill3

	def gen_stats(self):
		while self.points > 0:
			self.upper_points = randrange(2,7) if self.points > 7 else self.points
			self.points_to_perk = randrange(1, self.upper_points + 1)
			self.perknum = randrange(0, 7) 
			if self.stats[self.perks[self.perknum]] + self.points_to_perk <= 10:
				self.stats[self.perks[self.perknum]] += self.points_to_perk
				self.points -= self.points_to_perk
		return self.stats, sum(self.stats.values())

	def gen_char(self):
		# print("Your stats are: {},\
		# 		{}, {}".format(self.stats, self.skills, self.traits))
		return self.gen_traits(), self.gen_skills(), self.gen_stats()

p1 = Generator()
print(p1.gen_char())
print(p1.gen_stats())
