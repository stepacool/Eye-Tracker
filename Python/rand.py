from random import randrange, choice

def randomizer():
	optional_trait_1 = 0
	optional_trait_2 = 0
	while optional_trait_1 == optional_trait_2:
		optional_trait_1 = randrange(0, 16)
		optional_trait_2 = randrange(0, 16)
	gifted = 1 if optional_trait_2 == 7 or optional_trait_1 == 7 else 0
	points = 33
	perks = ['ST', 'PE', 'EN', 'CH', 'IN', 'AG', 'LK']
	stats = { 
		"ST" : 1,
		"PE" : 1,
		"EN" : 1,
		"CH" : 1,
		"IN" : 1,
		"AG" : 1,
		"LK" : 1,
	}
	traits = ['Bloody Mess', 'Bruiser', 'Chem Reliant', 'Chem Resistant',
	'Fast Metabolism', 'Fast Shot', 'Finesse', 'Gifted', 'Good Natured',
	'Heavy Handed', 'Jinxed', 'Kamikaze', 'One Hander', 'Sex Appeal', 'Skilled', 'Small Frame']
	skills = ['Small Guns', 'Big Guns ', 'Energy Weapons', 'Unarmed', 'Melee Weapons',
	'Throwing ', 'First Aid', 'Doctor', 'Sneak', 'Lockpick', 'Steal', 'Traps', 'Science',
	'Repair', 'Speech', 'Barter', 'Gambling', 'Outdoorsman']
	skill1 = 0
	skill2 = 0
	skill3 = 0
	while skill1 == skill2 or skill2 == skill3 or skill3 == skill1:
		skill1, skill2, skill3 = choice(skills), choice(skills), choice(skills)
	if gifted:
		for i in stats.keys():
			stats[i] += 1
	while points > 0:
		upper_points = randrange(2,7) if points > 7 else points
		points_to_perk = randrange(1, upper_points + 1)
		perknum = randrange(0, 7) 
		if stats[perks[perknum]] + points_to_perk <= 10:
			stats[perks[perknum]] += points_to_perk
			points -= points_to_perk
	optional_trait_1 = traits[optional_trait_1]
	optional_trait_2 = traits[optional_trait_2]
	if optional_trait_2 == "Bruiser" or optional_trait_1 == "Bruiser":
		stats["ST"] += 2
	if optional_trait_1 == "Small Frame" or optional_trait_2 == "Small Frame":
		stats["AG"] += 1
	print("Stats: ", stats)
	print("Optional traits: {}, {}".format(optional_trait_1, optional_trait_2))
	print("Skills: {}, {}, {} \n".format(skill3, skill2, skill1),)

if __name__ == "__main__":
	while True:
		randomizer()