import unittest
import sys
sys.path.append("../code")
from StepLists import *


class TestStep(unittest.TestCase):
	def test_Step_init_method(self):
		step = Step('test','replace',['t', 'T'])
		self.assertEqual(step.components ,  ['test','replace',['t', 'T']])
		step = Step()
		self.assertEqual(step.components ,  [])


	def test_Step_execute_method_started_with_a_function(self):		
		step = Step(sum, [[1,2]])
		self.assertEqual(step.perform() ,  3)
		
		step = Step(str,['1'],'find',['1'])
		self.assertEqual(step.perform() ,  0	)
		
		step = Step(str,['1'],'__doc__')
		self.assertEqual(step.perform() ,  '1'.__doc__	)
		
		step = Step(str,['1'],'__doc__', 'lower',[])
		self.assertEqual(step.perform() ,  '1'.__doc__.lower())
		
		step = Step(str,['1'], 'lower',[],'__doc__')
		self.assertEqual(step.perform() ,  '1'.lower().__doc__	)
		
	def test_Step_execute_method_started_with_an_object(self):		
		step = Step('test','__doc__')
		self.assertEqual(step.perform() ,  'TesT'.__doc__)
		
		step = Step('test','replace',['t', 'T'])
		self.assertEqual(step.perform() ,  'TesT')
		
		step = Step('test','replace',['t', 'T'],'replace',['T', 't'])
		self.assertEqual(step.perform() ,  'test')
		
		step = Step('test','replace',['t', 'T'],'__doc__')
		self.assertEqual(step.perform() ,  'test'.__doc__)
		
		step = Step('test','__doc__','lower',[])
		self.assertEqual(step.perform() ,  'test'.__doc__.lower())


class TestFunctions(unittest.TestCase):
	def test_get_value_function(self):		
		self.assertEqual(get_value(0), 0)		
		self.assertEqual(get_value(Step('test','find',['t'])), 0)

	def test_if_function(self):
		igual = Step(str,['igual'])
		diferente = Step(str,['diferente'])
		self.assertEqual(if_(1, '==', 2, StepList(igual.components), StepList(diferente.components)) ,  False)
		self.assertEqual(if_('t', 'in', Step(list,['teste']), StepList(igual.components), StepList(diferente.components)) ,  True)

	def test_perform_the_list_of_arguments_function(self):
		string = perform_the_list_of_arguments([Step('','join',[[Step('','join',[['tes','te']]),'concluido']])])
		self.assertEqual(string ,  ['testeconcluido'])
		

class TestStepList(unittest.TestCase):	
	def test_StepList_execute_method(self):
		step_list=StepList(
					Step(print, ['']),
					Step(if_,[1,'is',1,
						StepList(
							Step()
						)
					,
						StepList(
							Step()
						)
					])
				)
		self.assertEqual(step_list.execute() ,  True)




if __name__ == '__main__':
    unittest.main()








