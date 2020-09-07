from datetime import datetime, date, timedelta

from builtins import print
from pymysql import cursors, connect

import constants
import revision_controller
from config import MYSQL_CONNECTION_INFO

#keyword 의 category 별 weight 를 읽어오는 함수
#category id를 key로 category의 weight를 value로 하는 dictionary 반환
def get_keyword_weight():

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            query = "SELECT * FROM  keyword_category"

            cursor.execute(query)

            keyword_weight_dic = {}

            categorys = cursor.fetchall()

    finally:
        connection.close()

    for category in categorys:
        id = int(category["id"])
        weight = float(category["weight"])
        keyword_weight_dic[id] = weight

    return keyword_weight_dic

#모든 문제의 keyword와 해당 category를 받아오는 함수
#keyword id를 key로 해당 category id를 value로 하는 dictionary 반환
def get_keyword_dic():

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            query = "SELECT * FROM keyword order by id asc"

            cursor.execute(query)

            keyword_dic = {}

            keywords = cursor.fetchall()

    finally:
        connection.close()

    for keyword in keywords:
        id = int(keyword["id"])
        category_id = int(keyword["category"])
        keyword_dic[id] = category_id

    return keyword_dic

#question의 id를 parameter로 받으면 question의 keyword list를 반환
#(,)로 구분 된 string을 한 칸에 한 keyword id를 담은 list로 제작
def get_question_keyword(question_id):

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    keyword_list = []

    try:
        with connection.cursor() as cursor:

            query = ("SELECT keyword FROM question WHERE id=" + str(question_id))

            cursor.execute(query)

            keyword = ""

            for item in cursor:
                keyword = item["keyword"]

            keyword_list = keyword.strip().split(",")

    finally:
        connection.close()

        return keyword_list

#학생 vector를 구하는 main 함수
def student_vector():

    keyword_category_weight = get_keyword_weight()
    keyword_dic = get_keyword_dic()

    keyword_count = 0

    #전체 keyword의 수를 구한다 -> 이는 벡터의 요소 수가 된다.
    for id in keyword_dic:
        if keyword_count < id:
            keyword_count = id

    revision_id = revision_controller.set_new_revision()

    student_dic = {}

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    #해당 날짜 내에 오답 내역을 받아온다.
    try:
        with connection.cursor() as cursor:

            query = "SELECT cdate FROM revision WHERE id = " + str(revision_id)

            cursor.execute(query)

            for item in cursor:
                end_date = item['cdate']

            start_date = end_date - timedelta(days = constants.target_date_length)

            cursor.execute("""SELECT * FROM student_incorrect WHERE cdate <= %s and cdate >= %s """, (str(end_date), str(start_date)))

            items = cursor.fetchall()

    finally:
            connection.close()

    #각 학생이 틀린 문제 수에 따라 각 keyword의 값을 추가
    for item in items:
        student_id = item['student_id']
        question_id = item['question_id']
        question_keyword_list = get_question_keyword(question_id)

        if student_dic.__contains__(student_id):

            student_dic[student_id][0] += 1

            for keyword in question_keyword_list:
                student_dic[student_id][int(keyword)] += 1
        else:

            student_vector_list = [0.0] * (keyword_count + 1)
            student_vector_list[0] = 1
            student_dic[student_id] = student_vector_list

            for keyword in question_keyword_list:
                student_dic[student_id][int(keyword)] += 1

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    #각 벡터 값을 전체 오답수로 나누고, category의 weight를 곱한다.
    #완성 된 vector를 student_vector table에 insert
    try:
        with connection.cursor() as cursor:

            for student_id in student_dic:

                incorrect_count = student_dic[student_id][0]

                vector = ""

                for num in range(1, keyword_count + 1):

                    if keyword_dic.__contains__(num):
                        student_dic[student_id][num] *= keyword_category_weight[keyword_dic[num]]
                        student_dic[student_id][num] /= incorrect_count

                    if num == 1:
                        vector += str(round(student_dic[student_id][num],constants.number_of_decimal))
                    else:
                        vector += ", "
                        vector += str(round(student_dic[student_id][num],constants.number_of_decimal))

                query = ("INSERT INTO student_vector(student_id, vector, revision, cdate) "
                            "VALUES (%s, %s, %s, %s)")

                args = (str(student_id), vector, str(revision_id), datetime.now())

                cursor.execute(query, args)

            connection.commit()

    finally:
        connection.close()

    return revision_id
