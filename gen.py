import random

LEN=5

with open('sample.tsv', 'w') as f:
	for i in range(LEN):
		if random.random() < 0.8: f.write(f'<p{i}>\t<parent>\t<c{i}_0>\t.\n')
		if random.random() < 0.8: f.write(f'<p{i}>\t<parent>\t<c{i}_1>\t.\n')
		if random.random() < 0.8: f.write(f'<c{i}_0>\t<sibling>\t<c{i}_1>\t.\n')
		if random.random() < 0.8: f.write(f'<c{i}_1>\t<sibling>\t<c{i}_0>\t.\n')

	for i in range(LEN):
		for j in range(i+1, LEN, 1):
			if random.random() < 0.4: 
				k = random.random()
				l = random.random()
				if l < 0.5:
					i, j = j, i
				if k < 0.25:
					f.write(f'<c{i}_0>\t<friend>\t<c{j}_0>\t.\n')
				elif k < 0.5:
					f.write(f'<c{i}_0>\t<friend>\t<c{j}_1>\t.\n')
				elif k < 0.75:
					f.write(f'<c{i}_1>\t<friend>\t<c{j}_0>\t.\n')
				else:
					f.write(f'<c{i}_1>\t<friend>\t<c{j}_1>\t.\n')

