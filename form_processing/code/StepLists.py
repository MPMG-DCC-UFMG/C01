import os
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import Select

 
def get_value(object):
	"""Checks if "object" is a Step object. If it is, it returns object.perform(), if not, it return the object itself.
	Parameters:
		object -- any object
	"""
	if type(object) == Step:
		return object.perform()
	else:
		return object


def performed_argument_list(object_list):	
	"""Iterates through the "object_list" executing every Step found and calling recursively this function for other lists found.
    Parameters:
		object_list -- a list
	"""
	for i in range(len(object_list)):
		object_list[i] = get_value(object_list[i])
		if type(object_list[i]) == list:
			object_list[i] = performed_argument_list(object_list[i])
	return object_list



def if_(value_1, comp, value_2, if_steps, else_steps):
	"""Simulates an if comparing the "value_1" with the "value_2" and after that it executes "if_steps" if the comparation returns true, 
	and "else_steps" otherwise.
	Parameters:
		value_1 -- first comparison value.
		comp -- string with the comparison symbol. Ex: '==', 'in' ...
		value_2 -- second comparison value.
		if_steps -- StepList object with the steps to be executed if the comparation returns True.
		else_steps -- StepList object with the steps to be executed if the comparation returns False.
	Returns:
		It returns the comparison result.
	"""

	cond_1 = get_value(value_1)
	cond_2 = get_value(value_2)

	d = {'cond_1': cond_1, 'cond_2': cond_2, 'execute': StepList.execute, 'if_steps' : if_steps, 'else_steps': else_steps}
	exec('if cond_1 '+comp+' cond_2:\n'+
		'	execute(if_steps)		\n'+
		'	retorno = True 			\n'+
		'else:						\n'+
		'	execute(else_steps)	\n'+
		'	retorno = False			\n', d)
	return d['retorno']



def for_pages_in(driver, url_list, steps):
	"""Iterates through the "url_list", loading each URL in the drive and for each one executes the "steps".
	Parameters:
		driver -- WebDriver being used for processing forms
		url_list -- List of URLs to be iterated 
		steps -- StepList to be executed for each URL loaded on drive
	"""
	for url in url_list:
		driver.get(url)
		steps.execute()
	


def select(driver, select_xpath, steps, valid_range=None): #documentado
	"""For each select option but only in the "valid_range", set this option on select by "driver" and execute the StepList "steps".
	Parameters:
		driver -- WebDriver being used for processing forms
		select_xpath -- Xpath of the select to be iterated
		steps -- StepList to be executed for each option to be selected
	"""
	select_element = Select(driver.find_element_by_xpath(select_xpath))
	option_list = driver.find_elements_by_xpath(select_xpath + '/option')
	if valid_range == None:
		valid_range = range(len(option_list))
	for option in valid_range:
		select_element = Select(driver.find_element_by_xpath(select_xpath))
		select_element.select_by_index(option)
		steps.execute()

class Step:
	def __init__(self, *components): 
		"""Creates an intance of Step.
		Parameters:
			components -- Step components. The structure of these components is better explained in the documentation.
		"""
		self.components = list(components)



	def perform(self):
		"""
		Executes the Step
		"""
		if not self.components:
			return None
		pos=0
		if callable(self.components[pos]):
			step_return = self.components[pos]( *performed_argument_list(self.components[pos+1]))
			pos = pos + 1
		else:
			step_return = self.components[pos]
		pos = pos+1
		while pos < len(self.components):		
			call = getattr(type(step_return),self.components[pos])
			if callable(call):		
				step_return = call(step_return, *performed_argument_list(self.components[pos+1]))
				pos = pos + 1
			else:
				step_return = getattr(step_return,self.components[pos])
			pos = pos+1
		return step_return


class StepList():

	def __init__(self, *steps):
		"""Creates an intance of StepList.
		Parameters:
			steps -- steps that compose this StepList.
		"""
		self.steps = list(steps)

	def execute(self): 
		"""
		Executes the step list, step by step.
		"""
		current_return = 0
		if not self.steps:
			return None
		for step in self.steps:
			if type(step) == Step:
				current_return = step.perform()
		return current_return

