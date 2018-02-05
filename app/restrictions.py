class Restrictions:
    Schools = ['Tufts University', 'University of Rhode Island']
    Courses = ['COMP40', 'COMP105', 'CSC106', 'CSC110', 'CSC201', 'CSC211', 'CSC212', 'CSC301', 'CSC305', 'CSC340', 'CSC411', 'CSC412', 'CSC415', 'CSC440']
    Mapping = {'Tufts University':['COMP40', 'COMP105'], 'University of Rhode Island':['CSC106', 'CSC110', 'CSC201', 'CSC211', 'CSC212', 'CSC301', 'CSC305', 'CSC340', 'CSC411', 'CSC412', 'CSC415', 'CSC440']}

    @staticmethod
    def choices_format(choice):
    	return list(map(lambda x: (x,x), choice))
