from mip import Var, Model, BINARY, INTEGER, xsum, OptimizationStatus, CBC, GRB, model
import numpy as np
import glob
import gurobipy as gp

import pandas as pd

class TimetablingModel:
    __slots__ = ['model', 'x']

    def __init__(self, model, x):
        self.model = model
        self.x = x
    #print("class TimetablingModel")

class Inst:
    __slots__ = ['classes', 'professors', 'contents', 'days', 'times', 'compatible_professor', 'class_credits', 'max_class_day']

    def __init__(self, classes, professors, contents, days, times, compatible_professor, class_credits, max_class_day):
        self.classes = classes #turmas
        self.professors = professors #professores
        self.contents = contents #disciplinas
        self.days = days #dias da semana
        self.times = times #horários
        self.compatible_professor = compatible_professor #horário disponíveis do professor
        self.class_credits = class_credits #carga horária de uma turma
        self.max_class_day = max_class_day #máximo de aulas que uma turma pode ter para uma matéria

def create_model(inst):

    model = Model("TimetablingModel", solver_name=GRB)

    classes, professors, contents, days, times, compatible_professor, class_credits, max_class_day = \
        inst.classes, inst.professors, inst.contents, inst.days, inst.times, inst.compatible_professor, \
        inst.class_credits, inst.max_class_day

    # variavel *x* indica se o professor p está atendendo, ou não, a turma c, no dia d, no horário h
    x = np.empty((len(class_credits), len(professors), len(days), len(times)), dtype=Var)
    for c, class_credit in class_credits.iterrows():
        for p, professor in professors.iterrows():
            if professor['Nome'] == class_credit['Professor']:
                for d, day in days.iterrows():
                    for t, time in times.iterrows():
                        x[c, p, d, t] = model.add_var(f"x({c},{p},{d},{t})", obj=0, var_type=BINARY)

    #(1) Colisão de professor: professor não pode lecionar mais de uma aula em um mesmo horário
    for p, professor in professors.iterrows():
        for c, class_credit in class_credits.iterrows():
            if professor['Nome'] == class_credit['Professor']:
                for d, day in days.iterrows():
                    model.add_constr(xsum(x[c, p, d, t]
                                          for t, time in times.iterrows())
                                             <= 1, name=f"1_{p},{d},{t}")

    #(2) Sobreposição de professores: Em um dia d e horário h, uma turma c tem aula no máximo com um  único professor:
    for p, professor in professors.iterrows():
        for c, class_credit in class_credits.iterrows():
            if professor["Nome"] == class_credit["Professor"]:
                for d, day in days.iterrows():
                    model.add_constr(xsum(x[c, p, d, t]
                                          for t, time in times.iterrows()
                                         )
                                     <= 1, name=f"2_")

    #(3) Carga horária: Cada professor p deve ministrar exatamente um certo número de aulas semanais para uma dada turma c:
    for c, class_credit in class_credits.iterrows():
        model.add_constr(xsum(x[c, p, d, t]
                              for p, professor in professors.iterrows()
                              if professor["Nome"] == class_credit["Professor"]
                              for d, day in days.iterrows()
                              for t, time in times.iterrows())
                           ==
                         int(class_credit['Aulas Semanais']), name=f"3_{c}")

    #(4) Limite diário de aulas por matéria: Uma turma não pode ter mais do que um certo nº de aulas diárias
    # de uma mesma matéria:
    for md, max_c_d in max_class_day.iterrows():
        for c, class_credit in class_credits.iterrows():
            for p, professor in professors.iterrows():
                if professor["Nome"] == class_credit["Professor"]:
                    for d, day in days.iterrows():
                        model.add_constr(xsum(x[c, p, d, t]
                                for t, time in times.iterrows()
                                if max_c_d["Turma"] == class_credit["Turma"]
                                )
                               <=
                             int(max_c_d['Máximo diário de aulas']), name=f"4_{c}{p}")

    # #(5) Corresponde as indisponibilidades dos professores: Estas restriçõees encontram-se contempladas ao utilizarmos
    # # a matriz ri_pdt nas restrições (1)

    model.write("model.lp")
    model.optimize()

    tt_model = TimetablingModel(model, x)

    return tt_model

def print_active_vars(tt_model):
    for i in range(len(tt_model.model.vars)):
        if tt_model.model.vars[i].x > 0.001:
            print(tt_model.model.vars[i].name, tt_model.model.vars[i].x)


def read_instance(file_path):
    # print("read instance")
    days = pd.read_csv("Datasets/dias_da_semana.csv")

    times = pd.read_csv("Datasets/horario_de_aula.csv")

    professors = pd.read_csv("Datasets/professores.csv", delimiter=',')

    classes = pd.read_csv("Datasets/turmas.csv", delimiter=',')

    professor_availability = pd.read_csv("Datasets/professor_availability.csv", delimiter=',')


    class_credits = pd.read_csv("Datasets/ch.csv", delimiter=',')

    max_class_day = pd.read_csv("Datasets/md.csv", delimiter=',')


    # Um content corresponde a um conteúdo presente dentro da carga horária de um curso/turma.
    # É composto por uma turma c, disciplina s, professor p e numero de aulas cr
    contents = []
    for i, s_ch in class_credits.iterrows():
        c = s_ch[0] # c corresponde a turma(class)
        s = s_ch[1] #s corresponde a disciplina(subject)
        p = s_ch[2] #p corresponde ao professor(professor)
        cr = s_ch[3] #cr corresponde ao numero de aulas(credits)
        contents.append([])
        contents[-1].append((c, s, p, cr))

    inst = Inst(classes, professors, contents, days, times, professor_availability, class_credits, max_class_day)

    return inst

inst_teste = glob.glob('dataset/*.csv')
teste = read_instance(inst_teste)
tt_model = create_model(teste)
print_active_vars(tt_model)

