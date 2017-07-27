from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
import re
import itertools
import pycel
from pycel.excelcompiler import *
# from pycel.excelwrapper import ExcelOpxWrapper as ExcelWrapperImpl
# import pycel.excellib
# from pycel.excellib import *
# from pycel.excelutil import *
# from math import *
# from networkx.classes.digraph import DiGraph
# from networkx.drawing.nx_pydot import write_dot
# from networkx.drawing.nx_pylab import draw, draw_circular
# from networkx.readwrite.gexf import write_gexf
# from pycel.tokenizer import ExcelParser, f_token, shunting_yard
# import cPickle
# import logging
# import networkx as nx

def encode_conditions(conditions):
    for i in range(len(conditions)):
        conditions[i] = conditions[i].replace("(s)", '("s")')
        conditions[i] = conditions[i].replace("(r)", '("r")')
        exists = re.findall(r'(exists\(.*?\))', conditions[i], re.M | re.I)
        for j in range(len(exists)):
            conditions[i] = conditions[i].replace(exists[j], '\"' + exists[j] + '\"')
        for_each = re.findall(r'(foreach\(.*?\))', conditions[i], re.M | re.I)
        for j in range(len(for_each)):
            conditions[i] = conditions[i].replace(for_each[j], '\"' + for_each[j] + '\"')
    return conditions


def generate_quantifier_vector(quantifier, type='exists'):
    '''Receive an exist condition and generate a boolean vector based on it's condition
        Type can be either exists or for_each'''
    exp_in_paranth = re.findall(r'' + type + '\((.*?)\)', quantifier, re.M | re.I)
    exp_in_paranth = exp_in_paranth[0].split(",")

    vecs = re.findall(r'(.)\[.\]', exp_in_paranth[-1], re.M | re.I)
    condition_vec = "1 " if type == 'exists' else "0 "
    condition_vec += "in [1 if " + exp_in_paranth[-1] + " else 0 "
    for i in range(len(exp_in_paranth) - 1):
        condition_vec += "for " + exp_in_paranth[i] + " in range(len(" + vecs[i] + ")) "
    condition_vec += "]"
    return condition_vec


def decode_conditions(conditions):
    for i in range(len(conditions)):
        conditions[i] = conditions[i].replace('("s")', '(s)')
        conditions[i] = conditions[i].replace('("r")', '(r)')
        for quantifier in ['exists', 'foreach']:
            exists = re.findall(r'\"(' + quantifier + '\(.*?\))\"', conditions[i], re.M | re.I)
            for j in range(len(exists)):
                exists_with_indices = list(exists)
                entries = re.findall(r'(._.)', exists[j], re.M | re.I)
                for k in range(len(entries)):
                    exists_with_indices[j] = exists_with_indices[j].replace(entries[k],
                                                                            (entries[k].replace("_", "[") + "]"))
                if not (">" in exists_with_indices[j]) and not ("<" in exists_with_indices[j]):
                    exists_with_indices[j] = exists_with_indices[j].replace("=", "==")
                exists_with_indices[j] = generate_quantifier_vector(exists_with_indices[j], quantifier)
                conditions[i] = conditions[i].replace('\"' + exists[j] + '\"', exists_with_indices[j])

    return conditions


def parse_conditions(conds):
    conds = encode_conditions(conds)
    python_inputs = []
    for i in conds:
        print "**************************************************"
        print "Formula: ", i
        e = shunting_yard(i);
        # print "RPN: ", "|".join([str(x) for x in e])
        G, root = build_ast(e)
        python_inputs += [root.emit(G, context=None)]
        print "Python code: ", root.emit(G, context=None)
        print "**************************************************"
    return decode_conditions(python_inputs)


def classify_strategies_to_dimensions(strategies, dimensions_matrix, dimensions_rows_conds,
                                      dimensions_columns_conds):
    row = ""
    col = ""
    print "matrix="+str(dimensions_matrix)
    for t in strategies:
        s = tuple(t)
        exec "row =" + dimensions_rows_conds[0]
        exec "col =" + dimensions_columns_conds[0]
        dimensions_matrix[row][col][s] = dict()
    return dimensions_matrix


def create_dimensions_matrix(dimensions_rows_categories_names, dimensions_columns_categories_names):
    dimensions_matrix = {row_name: dict() for row_name in dimensions_rows_categories_names}
    print "create_dimensions_matrix" + str(dimensions_matrix)
    for row_name in dimensions_matrix:
        for col_name in dimensions_columns_categories_names:
            dimensions_matrix[row_name][col_name] = dict()
    print "create_dimensions_matrix" + str(dimensions_matrix)
    return dimensions_matrix


def calc_payments(dimensions_matrix, payment_conds):
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                # print "first level= "+str(row)+","+str(col)+":"+str(strategy)
                for row2 in dimensions_matrix:
                    dimensions_matrix[row][col][strategy][row2] = dict()
                    for col2 in dimensions_matrix[row2]:
                        dimensions_matrix[row][col][strategy][row2][col2] = dict()
                        for strategy2 in dimensions_matrix[row2][col2]:
                            dimensions_matrix[row][col][strategy][row2][col2][strategy2] = dict()
                            # print "second level= "+str(row)+","+str(col)+":"+str(strategy)+str(row2)+","+str(col2)+":"+str(strategy2)
                            s = strategy
                            r = strategy2
                            payment = 0
                            exec "payment=" + payment_conds[0]
                            dimensions_matrix[row][col][strategy][row2][col2][strategy2]["val"] = payment
                            # print "third level= " + str(row) + "," + str(col) + ":" + str(strategy) + str(
                            #     row2) + "," + str(col2) + ":" + str(strategy2)+"="+str(payment)
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                for row2 in dimensions_matrix[row][col][strategy]:
                    for col2 in dimensions_matrix[row][col][strategy][row2]:
                        cell_size = len(dimensions_matrix[row][col][strategy][row2][col2])
                        pyments_in_cell = [
                            eval(str(dimensions_matrix[row][col][strategy][row2][col2][strategy2]["val"])) for
                            strategy2
                            in dimensions_matrix[row][col][strategy][row2][col2]]
                        uni_payment = sum([(1 / float(cell_size)) * payment for payment in pyments_in_cell])
                        dimensions_matrix[row][col][strategy][row2][col2]["uniform_payment"] = uni_payment
                        # print "second level= " + str(row) + "," + str(col) + ":" + str(strategy) + str(
                        #     row2) + "," + str(col2) + ":" + str(len(dimensions_matrix[row][col][strategy][row2][col2]))+",uni="+str(uni_payment)
    # dimensions_matrix_copy = dict(dimensions_matrix)
    # for row in dimensions_matrix:
    #     for col in dimensions_matrix[row]:
    #         strategy = dimensions_matrix[row][col].keys()[0]
    #         for row2 in dimensions_matrix[row][col][strategy]:
    #             for col2 in dimensions_matrix[row][col][strategy][row2]:
    #                 if row==row2 and col==col2:
    #                     # a=1
    #                     dimensions_matrix_copy[row][col]["uniform_payment"]= dimensions_matrix[row][col][strategy][row2][col2]["uniform_payment"]
    # dimensions_matrix = dict(dimensions_matrix_copy)
    return dimensions_matrix


def calc_MD_eq(dimensions_matrix, dimensions_ordered_row, dimensions_ordered_col):
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                is_MD_eq = True
                row_index = dimensions_ordered_row.index(row)
                if row_index != 0:
                    if dimensions_matrix[row][col][strategy][row][col]["uniform_payment"] < \
                            dimensions_matrix[row][col][strategy][dimensions_ordered_row[row_index - 1]][col][
                                "uniform_payment"]:
                        is_MD_eq = False
                if row_index != len(dimensions_ordered_row) - 1:
                    if dimensions_matrix[row][col][strategy][row][col]["uniform_payment"] < \
                            dimensions_matrix[row][col][strategy][dimensions_ordered_row[row_index + 1]][col][
                                "uniform_payment"]:
                        is_MD_eq = False
                col_index = dimensions_ordered_col.index(col)
                if col_index != 0:
                    if dimensions_matrix[row][col][strategy][row][col]["uniform_payment"] < \
                            dimensions_matrix[row][col][strategy][row][dimensions_ordered_col[col_index - 1]][
                                "uniform_payment"]:
                        is_MD_eq = False
                if col_index != len(dimensions_ordered_col) - 1:
                    if dimensions_matrix[row][col][strategy][row][col]["uniform_payment"] < \
                            dimensions_matrix[row][col][strategy][row][dimensions_ordered_col[col_index + 1]][
                                "uniform_payment"]:
                        is_MD_eq = False
                if is_MD_eq:
                    dimensions_matrix[row][col][strategy]["is_MD_eq"] = True
                else:
                    dimensions_matrix[row][col][strategy]["is_MD_eq"] = False
    return dimensions_matrix


def calc_Global_eq(dimensions_matrix):
    is_Global_eq = False
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                if dimensions_matrix[row][col][strategy]["is_MD_eq"]:
                    is_Global_eq = True
                    for row2 in dimensions_matrix[row][col][strategy]:
                        if type(dimensions_matrix[row][col][strategy][row2]) != bool:
                            for col2 in dimensions_matrix[row][col][strategy][row2]:
                                if dimensions_matrix[row][col][strategy][row][col]["uniform_payment"] < \
                                        dimensions_matrix[row][col][strategy][row2][col2]["uniform_payment"]:
                                    is_Global_eq = False
                if is_Global_eq:
                    dimensions_matrix[row][col][strategy]["is_Global_eq"] = True
                else:
                    dimensions_matrix[row][col][strategy]["is_Global_eq"] = False
    return dimensions_matrix


# some test formulas
payment_conds1 = [
    # '=5*log(sin(6)+2)',
    # '=5*log(sin(3,7,9)+2)',
    # '=3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3',
    '=IF(exists(i,j,s_i=r_j),0,IF(LEN(s)=2,3,2))',
    # '=IF(foreach(i,j,s_i=r_j),0,IF(LEN(s)=2,3,2))',
    # '=IF(foreach(i,s_i=r_i),0,IF(LEN(s)=2,3,2))',
]
# some test formulas
dimensions_conds1 = [
    # '=5*log(sin(6)+2)',
    # '=5*log(sin(3,7,9)+2)',
    # '=3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3',
    '=IF(exists(i,s_i=3),"center","not center")',
    '=IF(len(s)>1,"two","one")',
    # '=IF(foreach(i,j,s_i=r_j),0,IF(LEN(s)=2,3,2))',
    # '=IF(foreach(i,s_i=r_i),0,IF(LEN(s)=2,3,2))',
]
#
# payment_conds = encode_conditions(payment_conds)
# print payment_conds
# python_inputs = []
# for i in payment_conds:
#     print "**************************************************"
#     print "Formula: ", i
#     e = shunting_yard(i);
#     # print "RPN: ", "|".join([str(x) for x in e])
#     G, root = build_ast(e)
#     python_inputs += [root.emit(G, context=None)]
#     print "Python code: ", root.emit(G, context=None)
#     print "**************************************************"
#
#
# print python_inputs
# payment_conds = parse_conditions(payment_conds1)
# print payment_conds
# print decode_conditions(python_inputs)
# dimensions_conds = parse_conditions(dimensions_conds)
# print dimensions_conds
# s = [2, 3]
# exec "print " + dimensions_conds[0]
strategies_vector1 = [[1], [2], [3], [4], [5], [1, 2], [2, 3], [3, 4], [4, 5]]
dimensions_rows_categories_names1 = {"dimensions_row_category_name_1": "center",
                                     "dimensions_row_category_name_2": "not center"}
dimensions_columns_categories_names1 = {"dimensions_column_category_name_1": "one",
                                        "dimensions_column_category_name_2": "two"}
dimensions_ordered_row1 = ["center", "not center"]
dimensions_ordered_col1 = ["one", "two"]
dimensions_rows_conds1 = [dimensions_conds1[0]]
dimensions_columns_conds1 = [dimensions_conds1[1]]


def generate_all_strategies_combinations(n,full_set):
    # Generate all combinations of size n from the set full_set
    full_set_list = []
    full_set_str = full_set.replace("{","[").replace("}","]")
    exec "full_set_list="+full_set_str
    return list(itertools.combinations(full_set_list, n))
def full_calc(strategies_vector, dimensions_rows_conds, dimensions_columns_conds, dimensions_rows_categories_names,
              dimensions_columns_categories_names, dimensions_ordered_row, dimensions_ordered_col, payment_conds):
    dimensions_rows_conds = parse_conditions(dimensions_rows_conds)
    dimensions_columns_conds = parse_conditions(dimensions_columns_conds)
    payment_conds = parse_conditions(payment_conds)
    print "dimensions_rows_categories_names"+str(dimensions_rows_categories_names)
    dimensions_matrix = create_dimensions_matrix(dimensions_rows_categories_names,
                                                 dimensions_columns_categories_names)
    print str(dimensions_matrix)
    dimensions_matrix = classify_strategies_to_dimensions(strategies_vector, dimensions_matrix,
                                                          dimensions_rows_conds,
                                                          dimensions_columns_conds)
    print dimensions_matrix
    dimensions_matrix = calc_payments(dimensions_matrix, payment_conds)
    print "\n calc global eq"
    print "*************************************"
    dimensions_matrix = calc_MD_eq(dimensions_matrix, dimensions_ordered_row, dimensions_ordered_col)
    dimensions_matrix = calc_Global_eq(dimensions_matrix)
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                print str(row) + "," + str(col) + ":" + str(dimensions_matrix[row][col][strategy]["is_Global_eq"])
    print "\n calc MD eq"
    print "*************************************"
    for row in dimensions_matrix:
        for col in dimensions_matrix[row]:
            for strategy in dimensions_matrix[row][col]:
                print str(row) + "," + str(col) + ":" + str(dimensions_matrix[row][col][strategy]["is_MD_eq"])


class NameForm(forms.Form):
    strategies_vector_length = forms.CharField(max_length=100, required=False)
    strategies_full_set = forms.CharField(max_length=100, required=False)


    strategies_super_set = forms.CharField(max_length=100, required=False)
    strategies_lower_bound = forms.CharField(max_length=100, required=False)
    strategies_constraint_1 = forms.CharField(max_length=100, required=False)
    strategies_constraint_2 = forms.CharField(max_length=100, required=False)
    strategies_constraint_3 = forms.CharField(max_length=100, required=False)
    strategies_constraint_4 = forms.CharField(max_length=100, required=False)
    strategies_constraint_5 = forms.CharField(max_length=100, required=False)
    strategies_constraint_6 = forms.CharField(max_length=100, required=False)
    strategies_constraint_7 = forms.CharField(max_length=100, required=False)
    strategies_constraint_8 = forms.CharField(max_length=100, required=False)
    strategies_constraint_9 = forms.CharField(max_length=100, required=False)
    strategies_constraint_10 = forms.CharField(max_length=100, required=False)

    payment_if_cond_1 = forms.CharField(max_length=100, required=False)
    payment_if_true_1 = forms.CharField(max_length=100, required=False)
    payment_if_false_1 = forms.CharField(max_length=100, required=False)
    payment_if_cond_2 = forms.CharField(max_length=100, required=False)
    payment_if_true_2 = forms.CharField(max_length=100, required=False)
    payment_if_false_2 = forms.CharField(max_length=100, required=False)
    payment_if_cond_3 = forms.CharField(max_length=100, required=False)
    payment_if_true_3 = forms.CharField(max_length=100, required=False)
    payment_if_false_3 = forms.CharField(max_length=100, required=False)
    payment_if_cond_4 = forms.CharField(max_length=100, required=False)
    payment_if_true_4 = forms.CharField(max_length=100, required=False)
    payment_if_false_4 = forms.CharField(max_length=100, required=False)
    payment_if_cond_5 = forms.CharField(max_length=100, required=False)
    payment_if_true_5 = forms.CharField(max_length=100, required=False)
    payment_if_false_5 = forms.CharField(max_length=100, required=False)
    payment_if_cond_6 = forms.CharField(max_length=100, required=False)
    payment_if_true_6 = forms.CharField(max_length=100, required=False)
    payment_if_false_6 = forms.CharField(max_length=100, required=False)
    payment_if_cond_7 = forms.CharField(max_length=100, required=False)
    payment_if_true_7 = forms.CharField(max_length=100, required=False)
    payment_if_false_7 = forms.CharField(max_length=100, required=False)
    payment_if_cond_8 = forms.CharField(max_length=100, required=False)
    payment_if_true_8 = forms.CharField(max_length=100, required=False)
    payment_if_false_8 = forms.CharField(max_length=100, required=False)
    payment_if_cond_9 = forms.CharField(max_length=100, required=False)
    payment_if_true_9 = forms.CharField(max_length=100, required=False)
    payment_if_false_9 = forms.CharField(max_length=100, required=False)
    payment_if_cond_10 = forms.CharField(max_length=100, required=False)
    payment_if_true_10 = forms.CharField(max_length=100, required=False)
    payment_if_false_10 = forms.CharField(max_length=100, required=False)

    dimensions_row_category_name_1 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_2 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_3 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_4 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_5 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_6 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_7 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_8 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_9 = forms.CharField(max_length=100, required=False)
    dimensions_row_category_name_10 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_1 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_1 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_1 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_2 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_2 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_2 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_3 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_3 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_3 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_4 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_4 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_4 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_5 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_5 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_5 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_6 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_6 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_6 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_7 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_7 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_7 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_8 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_8 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_8 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_9 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_9 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_9 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_cond_10 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_true_10 = forms.CharField(max_length=100, required=False)
    dimensions_row_if_false_10 = forms.CharField(max_length=100, required=False)

    dimensions_column_category_name_1 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_2 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_3 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_4 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_5 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_6 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_7 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_8 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_9 = forms.CharField(max_length=100, required=False)
    dimensions_column_category_name_10 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_1 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_1 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_1 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_2 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_2 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_2 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_3 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_3 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_3 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_4 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_4 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_4 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_5 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_5 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_5 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_6 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_6 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_6 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_7 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_7 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_7 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_8 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_8 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_8 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_9 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_9 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_9 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_cond_10 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_true_10 = forms.CharField(max_length=100, required=False)
    dimensions_column_if_false_10 = forms.CharField(max_length=100, required=False)

    strategies_vector_1 = forms.CharField(max_length=100, required=False)
    strategies_vector_2 = forms.CharField(max_length=100, required=False)
    strategies_vector_3 = forms.CharField(max_length=100, required=False)
    strategies_vector_4 = forms.CharField(max_length=100, required=False)
    strategies_vector_5 = forms.CharField(max_length=100, required=False)
    strategies_vector_6 = forms.CharField(max_length=100, required=False)
    strategies_vector_7 = forms.CharField(max_length=100, required=False)
    strategies_vector_8 = forms.CharField(max_length=100, required=False)
    strategies_vector_9 = forms.CharField(max_length=100, required=False)
    strategies_vector_10 = forms.CharField(max_length=100, required=False)
    strategies_vector_11 = forms.CharField(max_length=100, required=False)
    strategies_vector_12 = forms.CharField(max_length=100, required=False)
    strategies_vector_13 = forms.CharField(max_length=100, required=False)
    strategies_vector_14 = forms.CharField(max_length=100, required=False)
    strategies_vector_15 = forms.CharField(max_length=100, required=False)
    strategies_vector_16 = forms.CharField(max_length=100, required=False)
    strategies_vector_17 = forms.CharField(max_length=100, required=False)
    strategies_vector_18 = forms.CharField(max_length=100, required=False)
    strategies_vector_19 = forms.CharField(max_length=100, required=False)
    strategies_vector_20 = forms.CharField(max_length=100, required=False)
    strategies_vector_21 = forms.CharField(max_length=100, required=False)
    strategies_vector_22 = forms.CharField(max_length=100, required=False)
    strategies_vector_23 = forms.CharField(max_length=100, required=False)
    strategies_vector_24 = forms.CharField(max_length=100, required=False)
    strategies_vector_25 = forms.CharField(max_length=100, required=False)
    strategies_vector_26 = forms.CharField(max_length=100, required=False)
    strategies_vector_27 = forms.CharField(max_length=100, required=False)
    strategies_vector_28 = forms.CharField(max_length=100, required=False)
    strategies_vector_29 = forms.CharField(max_length=100, required=False)
    strategies_vector_30 = forms.CharField(max_length=100, required=False)


def convert_nested_ifs_to_strings(nested_if):
    #Converts all #<num> to \"#num\", for the excel unwrapper
    hastags = re.findall(r'(\#\d+)', nested_if, re.M | re.I)
    for hashtag in hastags:
        nested_if = nested_if.replace(hashtag,"\""+hashtag+"\"")
    return nested_if
# def read_costraints(excel_constraints):
#     python_constraints = [0 for i in range(len(excel_constraints))]
#     for i in range(len(excel_constraints)):
#         e = shunting_yard(excel_constraints[i])
#         G, root = build_ast(e)
#         python_constraints[i] = root.emit(G, context=None)
#     return python_constraints

@csrf_exempt
def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            a = "if_cond_1 = "+str(form.cleaned_data['strategies_constraint_1'])
            b = "\nform.cleaned_data = " + str(form.cleaned_data)+"\n"
            strategies_constraints = dict()
            for datum in form.cleaned_data:
                if "constraint" in datum:
                    strategies_constraints[datum] = form.cleaned_data[datum]
            payment_conds = dict()
            for datum in form.cleaned_data:
                if ("payment" in datum) and ("cond" in datum):
                    payment_conds[datum] = form.cleaned_data[datum]
            dimensions_rows_conds_dict = dict()
            for datum in form.cleaned_data:
                if ("dimension" in datum) and ("row" in datum) and ("cond" in datum):
                    if str(form.cleaned_data[datum]) != '':
                        dimensions_rows_conds_dict[datum] = str("="+form.cleaned_data[datum])
                    else:
                        dimensions_rows_conds_dict[datum] = str(form.cleaned_data[datum])
            dimensions_rows_conds=[]
            for cond in dimensions_rows_conds_dict:
                if dimensions_rows_conds_dict[cond]!='':
                    dimensions_rows_conds +=[dimensions_rows_conds_dict[cond]]
            dimensions_columns_conds_dict = dict()
            for datum in form.cleaned_data:
                if ("dimension" in datum) and ("column" in datum) and ("cond" in datum):
                    if str(form.cleaned_data[datum]) != '':
                        dimensions_columns_conds_dict[datum] = str("="+form.cleaned_data[datum])
                    else:
                        dimensions_columns_conds_dict[datum] = str(form.cleaned_data[datum])
            dimensions_columns_conds=[]
            for cond in dimensions_columns_conds_dict:
                if dimensions_columns_conds_dict[cond]!='':
                    dimensions_columns_conds +=[dimensions_columns_conds_dict[cond]]
            strategies_vectors_str = dict()

            strategies_vectors = []
            for datum in form.cleaned_data:
                if ("vector" in datum):
                    strategies_vectors_str[datum] = form.cleaned_data[datum]
                    if str(strategies_vectors_str[datum]) != '':
                        strategies_vectors+= [[eval(str(strategies_vectors_str[datum]))]]
                    # strat_str = "strategies_vectors[datum] =" + str(strategies_vectors[datum])
                    # exec(strat_str)
            strategies_vectors = [list(strategy[0]) if type(strategy[0])==tuple else strategy for strategy in strategies_vectors]
            print "strategies_vectors="+str(strategies_vectors)
            dimensions_rows_categories_names = []
            for i in range(1,11):
                field_name = "dimensions_row_category_name_"+str(i)
                if str(form.cleaned_data[field_name]) != '':
                    dimensions_rows_categories_names+=[form.cleaned_data[field_name]]
            dimensions_columns_categories_names = []
            for i in range(1, 11):
                field_name = "dimensions_column_category_name_" + str(i)
                if str(form.cleaned_data[field_name]) != '':
                    dimensions_columns_categories_names += [form.cleaned_data[field_name]]
            print str(dimensions_rows_conds)

            strategies_vector_length = 0
            strategies_full_set = ""
            for datum in form.cleaned_data:
                if ("strategies_vector_length" in datum):
                    strategies_vector_length = form.cleaned_data[datum]
                if ("strategies_full_set" in datum):
                    strategies_full_set = form.cleaned_data[datum]
            if strategies_vector_length == 0:

            # full_calc(strategies_vector1, dimensions_rows_conds1, dimensions_columns_conds1,dimensions_rows_categories_names1,dimensions_columns_categories_names1,dimensions_ordered_row1,dimensions_ordered_col1)

            full_calc(strategies_vectors, dimensions_rows_conds, dimensions_columns_conds,dimensions_rows_categories_names,dimensions_columns_categories_names,dimensions_ordered_row1,dimensions_ordered_col1,payment_conds1)
            return HttpResponse("\n\n"+str(dimensions_rows_conds))
                                # +"\n\n"+str(payment_conds)+str(strategies_vectors)+"\n\n"+str(dimensions_rows_categories_names)+"\n\n"+str(dimensions_columns_categories_names))
            #return HttpResponseRedirect('/thanks/')
        else:
            return HttpResponse("Bug")

    # return render(request, 'name.html', {'form': form})
def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)



