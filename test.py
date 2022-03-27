from posixpath import isabs
import subprocess
import json
from turtle import numinput
import pathlib
import rdflib

ENCODING = 'ascii'

class Triple:
	def __init__(self, elements: list):
		assert len(elements) == 3 and elements[1].startswith('<') and elements[1].endswith('>')
		self.subject = elements[0]
		self.relation = elements[1][1:-1]
		self.object = elements[2]
	def __str__(self):
		return f'{self.subject} {self.relation} {self.object}'
	def __repr__(self):
		return self.__str__()

class RuleAttr:
	def __init__(self, elements: list):
		assert len(elements) == 7
		self.head_coverage = elements[0]
		self.std_confidence = elements[1]
		self.pca_confidence = elements[2]
		self.positive_examples = elements[3]
		self.body_size = elements[4]
		self.pca_body_size = elements[5]
		self.functional_variables = elements[6]
	def __str__(self):
		return f'[Head Coverage: {self.head_coverage}, Std Confidence: {self.std_confidence}, PCA Confidence: {self.pca_confidence}, Examples: {self.positive_examples}, Body Size: {self.body_size}, PCA Body Size: {self.pca_body_size}, Functional Vars: {self.functional_variables}]'
	def __repr__(self):
		return self.__str__()

class Rule:
	def __init__(self, text: str, is_attr_present=True):
		assert '=>' in text and text.count('=>') == 1
		predicate, conclusion = text.split('=>')
		predicate = predicate.split()
		if is_attr_present:
			conclusion, *attr = conclusion.split('\t')
			assert len(predicate) % 3 == 0

		self.predicates = [Triple(predicate[i*3:i*3+3]) for i in range(len(predicate) // 3)]
		self.conclusion = Triple(conclusion.split())
		if is_attr_present:
			self.attr = RuleAttr(attr)
		else:
			self.attr = None
	def __str__(self):
		return (
			f'==========\n' +
			f'[CONCLUSION]\t{self.conclusion}\n' + 
			f'[PREDICATES]\n' +
			'\t' + '\n\t'.join([p.__str__() for p in self.predicates]) + '\n' +
			f'[ATTR] {self.attr}\n' +
			f'==========\n\n')
	def __repr__(self):
		return self.__str__()

if __name__ == '__main__':
	filename = 'sample.tsv'
	extra_rule_file = 'rules.json'
	config = 'config.json'

	cp = subprocess.run(['java', '-jar', 'amie-milestone-intKB.jar', '-oute', '-dpr', '-minis', '1', filename], capture_output=True)
	output = cp.stdout

	if cp.returncode != 0:
		print('[Error] An error happened.')
		print('\tOutput: ' + output)
		exit(1)

	# get rid of windows newlines
	output = output.replace(b'\r', b'')
	output = output.split(b'\n')

	# retrieve rules
	num_rules = int(output[-2].split(b' ')[0])

	rules = []
	if num_rules > 0:
		rules_text = output[-4-num_rules+1:-4]
		rules = [Rule(rule_text.decode(ENCODING)) for rule_text in rules_text]
	else:
		print('[Info] No rules were extracted.')
		exit(1)

	# add extra rules
	if extra_rule_file is not None:
		with open(extra_rule_file) as f:
			content = json.loads(f.read())
			for rule_text in content:
				rules.append(Rule(rule_text, is_attr_present=False))

	assert len(rules) > 0
	print(rules)

	# use sparql to complete missing links
	# TODO: integrate prefixes
	g = rdflib.Graph()
	g.parse(filename, format='ttl')
	base_dir = pathlib.Path(filename).absolute().parents[0].as_uri()

	# For each rule, search all of its predicates
	# If all the predicates hold, and the conclusion is not in the KB, show the conclusion as an added edge
	for rule in rules:
		q = g.query(f"""SELECT {rule.conclusion.subject} {rule.conclusion.object} WHERE {{""" + 

			'\n'.join([f'{predicate.subject} <{base_dir}/{predicate.relation}> {predicate.object} .' for predicate in rule.predicates]) +
			
			f"""MINUS {{
				{rule.conclusion.subject} <{base_dir}/{rule.conclusion.relation}> {rule.conclusion.object} .
			}}
			FILTER({rule.conclusion.subject} != {rule.conclusion.object})
			}}""")
		for r in q:
			print(f'[ADDED] {r[0].split("/")[-1]} {rule.conclusion.relation} {r[1].split("/")[-1]}')
		print()
	