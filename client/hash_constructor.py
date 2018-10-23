from hashlib import sha256
from random import randint


def get_random_tuple(max_size: int) -> tuple:
	first_num, second_num = 0,0
	while first_num == second_num:
		first_num = randint(0,max_size-1)
		second_num = randint(0,max_size-1)
		line_number = randint(0,max_size-1)
	return (first_num, second_num, line_number)

def construct_tuples(num_snippets: int, max_size: int) -> str:
	tuples = []
	for i in range(num_snippets):
		tuples.append((',').join([str(x) for x in get_random_tuple(max_size)]))
	string_tuples = ('|').join(tuples)
	return string_tuples

def get_snippet(max_size: int, data: str, first_num: str, second_num: str, line_number: str) -> str:
	offset = max_size*line_number
	first_num += offset
	second_num += offset
	if first_num < second_num:
		text_slice = data[first_num:second_num]
	else:
		text_slice = data[second_num:first_num]
	return text_slice

def generate_hash(text: str, data: str, max_size: int) -> str:
	tuples = text.split('|')
	hash_strings = []
	for item in tuples:
		tuple_array = [int(x) for x in item.split(',')]
		snippet = get_snippet(max_size, data, *tuple_array)
		hash_strings.append(snippet)
	prehashval = ('').join(hash_strings)
	hashval = sha256(prehashval.encode('utf-8')).hexdigest()
	return hashval	