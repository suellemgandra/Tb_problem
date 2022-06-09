from mip import Var, Model, BINARY, INTEGER, xsum, OptimizationStatus, CBC, GRB, model
import numpy as np
import glob
import gurobipy as gp

import pandas as pd

class TimetablingModel:
    __slots__ = ['model', 'x', 'ch', 'md']

    def __init__(self, model, x, ch):
        self.model = model
        self.x = x
        # self.ri = ri
        self.ch = ch
        # self.md = md

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

    #print("class Inst")

def create_model(inst):

    # print("create model")
    model = Model("TimetablingModel", solver_name=GRB)

    classes, professors, contents, days, times, compatible_professor, class_credits, max_class_day = \
        inst.classes, inst.professors, inst.contents, inst.days, inst.times, inst.compatible_professor, \
        inst.class_credits, inst.max_class_day

    # variavel *x* indica se o professor p está atendendo, ou não, a turma c, no dia d, no horário h
    x = np.empty((len(professors), len(class_credits), len(days), len(times)), dtype=Var)
    for p, professor in professors.iterrows():
        for c, class_credit in class_credits.iterrows():
            if professor['Nome'] == class_credit['Professor']:
                for d, day in days.iterrows():
                    for t, time in times.iterrows():
                        x[p, c, d, t] = model.add_var(f"x({p},{c},{d},{t})", obj=0, var_type=BINARY)

    # #variável *ri* retorna 1 se o professor p está disponível no dia d, horário h; 0 caso contrário
    # ri = np.empty((len(professors), len(days), len(times)), dtype=Var)
    # for p, professor in professors.iterrows():
    #     for d, day in days.iterrows():
    #         for t, time in times.iterrows():
    #             ri[p, d, t] = model.add_var(f'ri({p},{d},{t})', lb=0, obj=0, var_type=BINARY)

    #variável *ch* corresponde a carga horária semanal do professor p para a turma c
    ch = np.empty((len(professors), len(class_credits)), dtype=int)
    # for p, professor in professors.iterrows():
    #     for c, class_ in class_credits.iterrows():
    #         for i, s_ch in class_credits.iterrows():
    #             if class_['Ano'] == s_ch['Turma'] and professor['Nome'] == s_ch['Professor']:
    #                 ch[p, c] = s_ch['Nº Aulas Semanais']

    #variável *md* corresponde ao número máximo diário de aulas do professor p (responsável pela matária) para a turma c
    # md = np.empty((len(professors), len(classes)), dtype=int)
    # for p, professor in professors.iterrows():
    #     for professor[1] in max_class_day:
    #         for c, class_ in classes.iterrows():
    #             for i, md_p in max_class_day.iterrows():
    #                 if professor[1] == md_p[0] and class_[1] == md_p[1]:
    #                    md[p, c] = md_p[2]

    # #(1) Colisão de professor: professor não pode lecionar mais de uma aula em um mesmo horário
    # for p, professor in professors.iterrows():
    #     for d, day in days.iterrows():
    #         for t, time in times.iterrows():
    #             model.add_constr(xsum(x[p, c, d, t] for c, class_credit in class_credits.iterrows() if professor['Nome'] == class_credit['Professor']) <=
    #                             1, name=f"1_{p},{d},{t}")

    # #(2) Sobreposição de professores: Em um dia d e horário h, uma turma c tem aula no máximo com um  único professor:
    # for c, class_ in classes.iterrows():
    #     for d, day in days.iterrows():
    #         for t, time in times.iterrows():
    #             model.add_constr(xsum(x[p, c, d, t] for p in range(len(professors))) <= 1, name=f"2_")

    #(3) Carga horária: Cada professor p deve ministrar exatamente um certo número de aulas semanais para uma dada turma c:
    for c, class_credit in class_credits.iterrows():
        model.add_constr(xsum(x[c, p, d, t]
                             for p, professor in professors.iterrows()
                             if professor["Nome"] == class_credit["Professor"]
                             for d, day in days.iterrows()
                             for t, time in times.iterrows())
                        ==
                         2, name=f"3_{c}")
                        # int(class_credit['Aulas Semanais']), name="3_{c}")
    # for p, professor in professors.iterrows():
    #     for c, class_credit in class_credits.iterrows():
    #         model.add_constr(xsum(x[p, c, d, t] for d in range(len(days)) for t in range(len(times))) ==
    #                          ch[p, c], name=f"3_({p},{c}")

    # #(4) Limite diário de aulas por matéria: Uma turma não pode ter mais do que um certo nº de aulas diárias de uma mesma matéria:
    # for p, professor in professors.iterrows():
    #     for c, class_ in classes.iterrows():
    #         for d, day in days.iterrows():
    #             model.add_constr(xsum(x[p, c, d, t] for t in range(len(times))) == md[p, c], name=f"4_({p},{c})")
    #
    # #(5) Corresponde as indisponibilidades dos professores: Estas restriçõees encontram-se contempladas ao utilizarmos
    # # a matriz ri_pdt nas restrições (1)

    model.write("model.lp")
    model.optimize()

    tt_model = TimetablingModel(model, x, ch, md)

    return tt_model


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
teste_create = create_model(teste)



