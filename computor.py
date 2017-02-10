# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    computor.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aderuell <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/05/04 15:26:05 by aderuell          #+#    #+#              #
#    Updated: 2015/05/15 18:51:09 by aderuell         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #
# -*-coding:utf-8 -*

from sys import argv
from re import compile
from operator import attrgetter

re_space = compile(r"\s+")
re_polynom = compile(r"([+-])?((?:(?:[\d]+[.\/]?[\d]+)|(?:[\d]+)))?(?:[*]?)([Xx])?(?:[\^]{1}([+-]?[\d]+[\/.]?[\d]*))?")
re_letter = compile(r"[^\dxX^.\/*+=\-]+")

def error(code):
	if code == 1:
		print("- Invalid equation")
	if code == 2:
		print("The polynomial degree is stricly greater than 2, I can't solve.")
	if code == 3:
		print("I can't solve the equation...")
	if code == 4:
		print("There are forbidden characters")
	return False

def floatOrInt(string):
	if string.count(".") == 1:
		return float(string)
	elif string.count("/") == 1:
		ret = string.split(sep = '/')
		return float(int(ret[0]) / int(ret[1]))
	else:
		return int(string)

class Polynom():
	sign = None
	num = None
	x = False
	power = None

	def __init__(self, expression = None, sign = None, num = None, x = False, power = None):
		self.sign = sign
		self.num = num
		self.x = x
		self.power = power

		if expression != None:
			if expression.group(1) is not None:
				self.sign = expression.group(1)
			if expression.group(2) != None:
				self.num = floatOrInt(expression.group(2))
			if expression.group(3) == 'X' or expression.group(3) == 'x':
				self.x = True
				if expression.group(4) != None:
					self.power = int(expression.group(4))
				else:
					self.power = 1
			else:
				self.power = 0
			if self.x and self.power == 0:
				self.x = False
			if self.sign == None:
				self.sign = '+'
			if self.num == None:
				self.num = 1

	def toString(self, pos = 0):
		string = ""
		if pos != 0 or self.sign == '-':
			string = string + self.sign + " "
		if self.x and self.power != 0 and self.num == 1:
			if self.power == 1:
				string = string + "x"
			else:
				string = string + "x^" + str(self.power)
		elif self.x and self.power != 0 and self.num != 0:
			if self.power == 1:
				string = string + str(self.num) + "x"
			else:
				string = string + str(self.num) + "x^" + str(self.power)
		else:
			string = string + str(self.num)
		return string

	def getNum(self):
		if self.sign == '-':
			return -self.num
		return self.num

	def inverseSign(self):
		if self.sign == '-':
			self.sign = '+'
		else:
			self.sign = '-'
	


class Equation():
	left = []
	right = []

	def __init__(self):
		self.left = []
		self.right = []

	def parseEquation(self):
		#Basics verifications
		if len(equation) < 3 or equation.count("=") != 1:
			return error(1)

		i = 0
		before_equal = True
		while i < len(equation):
			if equation[i] == '=':
				i += 1
				before_equal = False

			#Keep polynome
			expression = re_polynom.match(equation, i)
			if expression == None:
				return error(1)
			try:
				p = Polynom(expression)
			except:
				return error(1)
			if before_equal:
				self.left.append(p)
			else:
				self.right.append(p)
			i += len(expression.group(0))
		if len(self.right) < 1 or len(self.left) < 1:
			return error(1)
		tmp = []
		for i, polynome in enumerate(self.left):
			if polynome.num == 0:
				tmp.append(polynome)
		for i, polynome in enumerate(tmp):
			self.left.remove(polynome)
		tmp = []
		for i, polynome in enumerate(self.right):
			if polynome.num == 0:
				tmp.append(polynome)
		for i, polynome in enumerate(tmp):
			self.right.remove(polynome)
		if len(self.right) == 0:
			zero = Polynom(None, '+', 0, False, 0)
			self.right.append(zero)
		if len(self.left) == 0:
			zero = Polynom(None, '+', 0, False, 0)
			self.left.append(zero)
		self.printEquation()
		return True

	def printEquation(self, text = "Equation :"):
		string = ""
		for i, polynome in enumerate(self.left):
			if i != 0:
				string = string + " " + polynome.toString(i)
			else:
				string = string + polynome.toString(i)
		string = string + " ="
		for i, polynome in enumerate(self.right):
			string = string + " " + polynome.toString(i)
		print(text,string)

	def reduceEquation(self):

		# Tout mettre du meme cote
		tmp = []
		for i, polynome in enumerate(self.right):
			tmp.append(polynome)
		self.right = []
		zero = Polynom(None, '+', 0, False, 0)
		self.right.append(zero)
		for i, polynome in enumerate(tmp):
			polynome.inverseSign()
			self.left.append(polynome)

		# Reduire l'expression
		for i, polynome in enumerate(self.left):
			tmp = []
			degree = polynome.power
			for j, elt in enumerate(self.left):
				if i != j and degree == elt.power:
					tmp.append(elt)
			for j, elt in enumerate(tmp):
				self.left.remove(elt)
				val = polynome.getNum() + elt.getNum()
				if val < 0:
					polynome.sign = '-'
					polynome.num = -val
				else:
					polynome.sign = '+'
					polynome.num = val
		tmp = []
		for i, polynome in enumerate(self.left):
			if polynome.num == 0:
				tmp.append(polynome)
		for i, polynome in enumerate(tmp):
			self.left.remove(polynome)

		# Organiser l'expression
		self.left = sorted(self.left, key=attrgetter("power"))
		self.left.reverse()

		if len(self.left) == 0:
			zero = Polynom(None, '+', 0, False, 0)
			self.left.append(zero)

		self.printEquation("Reduced form :")
		return True

	def resolveEquation(self):
		degree = 0
		for elt in self.left:
			if elt.power < 0:
				return error(3)
			if elt.power > degree:
				degree = elt.power
		print("Polynomial degree :", degree)
		if degree > 2:
			return error(2)
		elif degree == 2:
			if len(self.left) == 3:
				a = self.left[0].getNum()
				b = self.left[1].getNum()
				c = self.left[2].getNum()
			elif len(self.left) == 2:
				a = self.left[0].getNum()
				if self.left[1].power == 1:
					b = self.left[1].getNum()
					c = 0
				else:
					b = 0
					c = self.left[1].getNum()
			else:
				a = self.left[0].getNum()
				b = 0
				c = 0
			discriminant = (b * b) - (4 * a * c)
			print("Discriminant = ", discriminant)
			if discriminant > 0:
				print("Discriminant is strictly positive, the two solutions are :")
				print(str((-b - (discriminant ** 0.5)) / (2 * a)))
				print(str((-b + (discriminant ** 0.5)) / (2 * a)))
			elif discriminant == 0:
				print("Discriminant is 0, the solution is :")
				print(str(-b / (2 * a)))
			else:
				discriminant = -discriminant
				print("Discriminant is strictly negative, the two solutions are :")
				print(str(-b / (2 * a)), "- i *", str((discriminant ** 0.5) / 2 * a))
				print(str(-b / (2 * a)), "+ i *", str((discriminant ** 0.5) / 2 * a))
			return True
		elif degree == 1:
			if len(self.left) > 1:
				a = self.left[0].getNum()
				b = self.left[1].getNum()
			else:
				a = self.left[0].getNum()
				b = 0
			print("The solution is")
			print("-b/a =", str(-b/a))
			return True
		elif degree == 0:
			a = self.left[0].getNum()
			if a == 0:
				print("Every real are solution")
			else:
				print("No solution")
			return True
		else:
			return error(3)


#Main
del argv[0]
if len(argv) < 1:
	print('Not enough arguments')
	print('Usage ./computor.py <equation1> [<equation2> ...]')
else:
	for equation in argv:
		print("")
		print("-->",equation)
		equation = equation.replace(" ", "")
		if re_letter.search(equation) is not None:
			error(4)
			continue
		eq = Equation()
		if eq.parseEquation() is False:
			continue
		if eq.reduceEquation() is False:
			continue
		if eq.resolveEquation() is False:
			continue
