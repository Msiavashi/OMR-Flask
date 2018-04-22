import sympy
import statistics
import operator

class Corrector:
    def __init__(self, exam, number_of_question):
        self.exam = exam
        self.number_of_questions = number_of_question
        self.answer_status = {"correct": True, "wrong": False, "empty": None}


    def correct_exam(self):
        #TODO: Correct the exam
        pass

    def calculate_growth_for_all(self):
        pass



    def calculate_rank_for_all(self):
        pass


    def check_answers(self, student_answers):
        result = {}
        def is_correct(student_ans, correct_ans):
            if student_ans == correct_ans: return self.answer_status["correct"]
            elif student_ans == []: return self.answer_status["empty"]
            else: return self.answer_status["wrong"]
        for i in range(1, self.number_of_questions + 1):
            result[i] = is_correct(student_answers[i], self.exam.answers_key[i])

        return result



    def evaluate_answers_for_all(self):
        results = {}
        for workbook in self.exam.workbooks:
            if workbook.presence:   #if the workbook owner was present
                results[workbook.student_id] = self.check_answers(workbook.answers)
        return results


    def _calculate_percentage_for_single_student(self, evaluated_answers_dic):
        calculator = None
        result = {}
        def without_negative_point(num_correct_answers, num_wrong_answers, total_question):
            return (num_correct_answers * 100.0) / total_question

        def with_negative_point(num_correct_answers, num_wrong_answers, total_question):
            return (((num_correct_answers * 3.0) - (num_wrong_answers)) * 100.0 ) / (total_question * 3.0)

        if self.exam.setting.lessons["negative_point"]: calculator = with_negative_point
        elif not self.exam.setting.lessons["negative_point"]: calculator = without_negative_point


        for lesson_name, lesson_meta in self.exam.setting.lessons.items():
            range_start, range_end = lesson_meta["range"]
            correct_answers = len([i for i in evaluated_answers_dic if evaluated_answers_dic[i] and range_start <= i <= range_end])
            wrong_answers = len([i for i in evaluated_answers_dic if not evaluated_answers_dic[i] and range_start <= i <= range_end])
            result[lesson_name] = calculator(correct_answers, wrong_answers, range_end - range_start + 1)

        return result



    def _calculate_percentage_without_negative_point(self):
        pass

    def calculate_percentage_for_all_students(self, workbooks_evaluated_ans_dic):
        results = {}

        for workbook, evaluated_answers in workbooks_evaluated_ans_dic.items():
            results[workbook] = self._calculate_percentage_for_single_student(evaluated_answers)

        return results

    def calculate_overall_balance(self):
        #TODO: return the balance of a student
        pass

    def calculate_lesson_rank(self):
        #TODO: calculate ranks for each lesson
        pass

    def calculate_lessons_balance_for_all(self, workbooks_percentages_dic):
        #TODO: calculate balance for ech lesson

        workbooks_balances_dic = {}
        def get_mean(lesson):
            mean = 0.0
            for _, percentages in workbooks_percentages_dic.items():
                mean += percentages[lesson]
            mean = mean / len(workbooks_percentages_dic)
            return mean

        def get_standard_deviation(lesson):
            percents = []
            for _, percentages in workbooks_percentages_dic.items():
                percents.append(percentages[lesson])

            return statistics.stdev(percents)
        z, m, x, s = sympy.symbols("z m x s")
        T = 1000*z + 500    #balance formula
        Z = ( x - m ) / s      #z formula
        for workbook, percentages_dic in workbooks_percentages_dic.items():
            balances = {}
            for lesson, percent in percentages_dic.items():
                mean = get_mean(lesson)
                standard_deviation = get_standard_deviation(lesson)
                balance = T.subs(z, Z.subs([(m, mean), (s, standard_deviation), (x, percent)]))
                balances[lesson] = balance
            workbooks_balances_dic[workbook] = balances

        return workbooks_balances_dic

    def calculate_total_balance_for_all(self, workbooks_balances_dic):
        workbooks_total_balances_dic = {}
        balance = 0
        total_ratios = 0
        for lesson in self.exam.setting.lessons:
            total_ratios += lesson["ratio"]

        for workbook, balances in workbooks_balances_dic.items():
            for lesson, blaance in balances.items():
                balance += self.exam.setting.lessons[lesson]["ratio"] * balance
            workbooks_total_balances_dic[workbook] = balance / total_ratios

        return workbooks_total_balances_dic


    def calculate_lessons_ranks_for_all(self, workbooks_balances_dic):
        result = {}
        #initializing
        for workbook in workbooks_balances_dic:
            result[workbook] = {}

        #evaluation
        for lesson in self.exam.setting.lessons:
            workbook_ranks_tuple = sorted(workbooks_balances_dic.items(), key=lambda x: x[1][lesson])   #list of tuples
            for index, workbook, balance in enumerate(workbook_ranks_tuple):
                result[workbook][lesson] = index

        return result





# a = {'mohammad': {'arabi': 125, 'riazi': 5000}, 'ahmad': {'arabi': 400, 'riazi': 120}}
# test =  c = sorted(a.items(), key=lambda x: x[1]["riazi"])
# print test