
import csv
#import numpy as np
#import pandas as pd
#import requests

#read days of week
def read_days_week(file_path):
  file = csv.reader(open('Datasets/dias_da_semana.csv', mode='r', encoding='utf-8'), delimiter=",")
  D = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_day = l[0]
    day = l[1]
    D.append((id_day, day))
  return D

#read schedules
def read_class_schedules(file_path):
  file = csv.reader(open('Datasets/horario_de_aula.csv', mode='r', encoding='utf-8'), delimiter=",")
  H = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_schedule = l[0]
    meeting_time = l[1]
    period = l[2]
    H.append((id_schedule, meeting_time, period))
  return H

#read teachers
def read_teachers(file_path):
  file = csv.reader(open('Datasets/professores.csv', mode='r', encoding='utf-8'), delimiter=",")
  P = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_teacher = l[0]
    teacher = l[1]
    subject = l[2]
    workload = l[3]
    P.append((id_teacher, teacher, subject, workload))
  return P

#read courses
def read_classes(file_path):
  file = csv.reader(open('Datasets/turmas.csv', mode='r', encoding='utf-8'), delimiter=",")
  T = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_class = l[0]
    course = l[1]
    period = l[2]
    T.append((id_class, course, period))

  return T

#read teachers
def read_subjects(file_path):
  file = csv.reader(open('Datasets/subjects.csv', mode='r', encoding='utf-8'), delimiter=",")
  S = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_subject = l[0]
    subject = l[1]
    S.append((id_subject, subject))
  return S

#read teacher availability
def read_availability(file_path):
  file = csv.reader(open('Datasets/professor_availability.csv', mode='r', encoding='utf-8'), delimiter=",")
  ri = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_teacher = l[0]
    teacher = l[1]
    day = l[2]
    meeting_time = l[3]
    availability = l[4]
    ri.append((id_teacher, teacher, day, meeting_time, availability))
  return ri

#read course load
def read_course_load(file_path):
  file = csv.reader(open('Datasets/ch.csv', mode='r', encoding='utf-8'), delimiter=",")
  ch = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_course = l[0]
    course = l[1]
    subject = l[2]
    credits = l[3]
    ch.append((id_course, course, subject, credits))
  return ch

#read max class in the day
def read_max_class(file_path):
  file = csv.reader(open('Datasets/md.csv', mode='r', encoding='utf-8'), delimiter=",")
  md = []
  header = next(file)
  first_line = next(file)

  for l in file:
    id_subject = l[0]
    subject = l[1]
    course = l[2]
    max_class = l[3]
    md.append((id_subject, subject, course, max_class))
  return md

def read_class_subjects(file_parth):
  file = csv.reader(open('Datasets/class_subjects.csv', mode='r', encoding='utf-8'), delimiter=",")
  cs =[]
  header = next(file)
  first_line = next(file)

  for l in file:
      subject = l[0]
      course = l[1]
      cs.append((course, subject))
  return cs
