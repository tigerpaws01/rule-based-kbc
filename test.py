import subprocess
import json
from turtle import numinput
import rdflib

ENCODING = 'ascii'

class Triple:
	def __init__(self, elements: list):
		assert len(elements) == 3 and elements[1].startswith(b'<') and elements[1].endswith(b'>')
		self.subject = elements[0].decode(ENCODING)
		self.relation = elements[1].decode(ENCODING)
		self.object = elements[2].decode(ENCODING)
	def __str__(self):
		return f'{self.subject} {self.relation} {self.object}!!'
	def __repr__(self):
		return self.__str__()

class RuleAttr:
	def __init__(self, elements: list):
		assert len(elements) == 7
		self.head_coverage = elements[0].decode(ENCODING)
		self.std_confidence = elements[1].decode(ENCODING)
		self.pca_confidence = elements[2].decode(ENCODING)
		self.positive_examples = elements[3].decode(ENCODING)
		self.body_size = elements[4].decode(ENCODING)
		self.pca_body_size = elements[5].decode(ENCODING)
		self.functional_variables = elements[6].decode(ENCODING)
	def __str__(self):
		return f'[Head Coverage: {self.head_coverage}, Std Confidence: {self.std_confidence}, PCA Confidence: {self.pca_confidence}, Examples: {self.positive_examples}, Body Size: {self.body_size}, PCA Body Size: {self.pca_body_size}, Functional Vars: {self.functional_variables}]'
	def __repr__(self):
		return self.__str__()

class Rule:
	def __init__(self, text: str):
		assert b'=>' in text and text.count(b'=>') == 1
		predicate, conclusion = text.split(b'=>')
		predicate = predicate.split()
		conclusion, *attr = conclusion.split(b'\t')
		assert len(predicate) % 3 == 0

		self.predicates = [Triple(predicate[i*3:i*3+3]) for i in range(len(predicate) // 3)]
		self.conclusion = Triple(conclusion.split())
		self.attr = RuleAttr(attr)
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

	if num_rules > 0:
		rules_text = output[-4-num_rules+1:-4]
		rules = [Rule(rule_text) for rule_text in rules_text]
		print(rules)
	else:
		print('[Info] No rules were extracted.')

	# CompletedProcess(
	# 	args=['java', '-jar', 'amie-milestone-intKB.jar', '-oute', '-dpr', '-minis', '1', 'sample.tsv'], 
	# 	returncode=0, 
	# 	stdout=b'Assuming 9 as type relation\r\nLoading files... \n  Starting sample.tsv\n  Finished sample.tsv, still running: 0\nLoaded 40 facts in 10 ms using -1 MB\nUsing HeadCoverage as pruning metric with minimum threshold 0.01\r\nUsing recursivity limit 3\r\nDefault mining assistant that defines support by counting support on both head variables\r\nNo minimum threshold on standard confidence\r\nFiltering on PCA confidence with minimum threshold 0.1\r\nConstants in the arguments of relations are disabled\r\nPerfect rules pruning disabled\r\nMRT calls: 0\r\nStarting the mining phase... Using 16 threads\r\nRule\tHead Coverage\tStd Confidence\tPCA Confidence\tPositive Examples\tBody size\tPCA Body size\tFunctional variable\r\n?b  <sibling>  ?a   => ?a  <sibling>  ?b\t1\t1\t1\t20\t20\t20\t-1\r\n?a  <parent>  ?h  ?b  <sibling>  ?h   => ?a  <parent>  ?b\t1\t1\t1\t20\t20\t20\t-2\r\n?a  <parent>  ?g  ?g  <sibling>  ?b   => ?a  <parent>  ?b\t1\t1\t1\t20\t20\t20\t-2\r\n?g  <parent>  ?a  ?g  <parent>  ?b   => ?a  <sibling>  ?b\t1\t0.5\t0.5\t20\t40\t40\t-1\r\nMining done in 31 ms\r\nTotal time 64 ms\n4 rules mined.\r\n', stderr=b'Using the default schema relations\r\n')