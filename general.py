def cardNames() :
	suits = ['c']
	cards = []

	for card_num in range(1, 14) :
		for card_suit in suits :
			str_card = str(card_num) if card_num > 9 else '0' + str(card_num)  
			cards.append(str_card)
	return cards

class SolSet :
	image_names = cardNames()
	image_path = 'newCards'
	image_type = '.png'
	image_back = 'back'
	image_bottom = 'bottom'
	image_resolution = (80, 122)
	start_space = 10
	row_space = 30
	margin_space = 20
	tile_small_space = 25
	tile_large_space = 25
	double_speed = 500