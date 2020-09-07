from datetime import datetime, date, timedelta

from pymysql import cursors, connect

import constants
from config import MYSQL_CONNECTION_INFO
import revision_controller

#revision id를 넣으면 해당 학생 vector를 반환
#studendt id를 key로 vector를 value로 하는 dictionary 반환
#vector는 list
def get_student_vector(revision_id):

    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    student_vector_dic = {}

    try:
        with connection.cursor() as cursor:

            query = ("SELECT * FROM student_vector WHERE revision = " + str(revision_id))

            cursor.execute(query)

            items = cursor.fetchall()

    finally:
        connection.close()

    for item in items:
        student_id = item['student_id']
        vector = item["vector"]

        vector_list = vector.strip().split(",")
        student_vector_dic[student_id] = vector_list

    return student_vector_dic

#두 vector간의 유사도를 계산하는 함수
#두 vector는 list
# -1 ~ 1 사이의 값, 클수록 유사도가 높다
def get_cosine_similarity(vector_1, vector_2):

    numerator = 0.0
    vector_1_length = 0.0
    vector_2_length = 0.0

    index = 0

    for value in vector_1:
        numerator += (float(value) * float(vector_2[index]))
        vector_1_length += (float(value) * float(value))
        vector_2_length += (float(vector_2[index]) * float(vector_2[index]))
        index += 1

    result = numerator
    result /= (vector_1_length ** (0.5))
    result /= (vector_2_length ** (0.5))

    return result

#cluster의 center 정보가 같은 지 확인하는 함수
# 이전 시도에 비해서 cluster의 변화가 없는 지 확인한다.
def is_center_list_equal(before_center_list, after_center_list):

    result = True;

    list_length = before_center_list.__len__()

    for i in range(list_length):
        for j in range(list_length):
            if float(before_center_list[i][j]) != float(after_center_list[i][j]):
                result = False
                break

    return result

#clustering을 하는 main 함수
def student_clustering(revision_id):

    student_vector_dic = get_student_vector(revision_id)

    student_count = student_vector_dic.__len__()

    cluster_count = int(student_count / constants.cluster_size)

    #순서대로 cluster의 중심 값 저장
    cluster_center_list = []
    # cluster 의 list의 index를 key로 학생 id list를 값으로 가짐
    cluster_dic = {}

    loop_count  = 0

    #처음 학생 데이터 중에 선택 하여 cluster의 중심에 추가
    for student_id in student_vector_dic:
        if(loop_count < cluster_count):
            cluster_center_list.append(student_vector_dic[student_id])
            cluster_dic[loop_count] = []
            loop_count += 1
        else:
            break

    full_cluster_dic = {}
    remain_student_list = []

    for student_id in student_vector_dic:

        max_similarity = -2
        target_cluster = 0
        current_cluster = 0

        for cluster_vector in cluster_center_list:
            if not full_cluster_dic.__contains__(current_cluster):

                current_similarity = get_cosine_similarity(student_vector_dic[student_id], cluster_vector)

                if max_similarity < current_similarity:
                    target_cluster = current_cluster
                    max_similarity = current_similarity
            current_cluster += 1

        if max_similarity == -2:
            remain_student_list.append(student_id)
        else:
            cluster_dic[target_cluster].append(student_id)
            if(cluster_dic[target_cluster].__len__() >= constants.cluster_size):
                full_cluster_dic[target_cluster] = 0

    # 남은 학생이 있다면 배분
    full_cluster_dic.clear()

    for student_id in remain_student_list:

        max_similarity = -2
        target_cluster = 0
        current_cluster = 0

        for cluster_vector in cluster_center_list:
            if not full_cluster_dic.__contains__(current_cluster):
                current_similarity = get_cosine_similarity(student_vector_dic[student_id], cluster_vector)

                if max_similarity < current_similarity:
                    target_cluster = current_cluster
                    max_similarity = current_similarity

        current_cluster += 1

        cluster_dic[target_cluster].append(student_id)
        full_cluster_dic[target_cluster] = 0

    repeat_count = 0

    while repeat_count < constants.cluster_repeat_count:

        repeat_count += 1

        before_cluster_center = cluster_center_list.copy()

        # cluster center 재계산

        cluster_vector_size = cluster_center_list[0].__len__()

        cluster_center_list.clear()

        for cluster_index in cluster_dic:
            student_count = 0
            cluster_center = [0] * cluster_vector_size

            for student_id in cluster_dic[cluster_index]:
                vector_index = 0
                for student_value in student_vector_dic[student_id]:
                    cluster_center[vector_index] += float(student_value)
                    vector_index += 1
                student_count += 1

            for num in range(cluster_center.__len__()):
                cluster_center[num] /= float(student_count)

            cluster_center_list.append(cluster_center)

        #이전과 차이가 없으면 끝
        if is_center_list_equal(before_cluster_center, cluster_center_list):
            break

        #사용한 메모리 초기화
        full_cluster_dic.clear()
        remain_student_list.clear()

        loop_count = 0

        while(loop_count < cluster_count):
            cluster_dic[loop_count] = []
            loop_count += 1

        for student_id in student_vector_dic:

            max_similarity = -2
            target_cluster = 0
            current_cluster = 0

            for cluster_vector in cluster_center_list:
                if not full_cluster_dic.__contains__(current_cluster):

                    current_similarity = get_cosine_similarity(student_vector_dic[student_id], cluster_vector)

                    if max_similarity < current_similarity:
                        target_cluster = current_cluster
                        max_similarity = current_similarity
                current_cluster += 1

            if max_similarity == -2:
                remain_student_list.append(student_id)
            else:
                cluster_dic[target_cluster].append(student_id)
                if(cluster_dic[target_cluster].__len__() >= constants.cluster_size):
                    full_cluster_dic[target_cluster] = 0

        # 남은 학생이 있다면 배분
        full_cluster_dic.clear()

        for student_id in remain_student_list:

            max_similarity = -2
            target_cluster = 0
            current_cluster = 0

            for cluster_vector in cluster_center_list:
                if not full_cluster_dic.__contains__(current_cluster):
                    current_similarity = get_cosine_similarity(student_vector_dic[student_id], cluster_vector)

                    if max_similarity < current_similarity:
                        target_cluster = current_cluster
                        max_similarity = current_similarity

            current_cluster += 1

            cluster_dic[target_cluster].append(student_id)
            full_cluster_dic[target_cluster] = 0

    #clutering 이 종료 되면 db에 삽입
    connection = connect(host=MYSQL_CONNECTION_INFO['HOST'],
                         port=MYSQL_CONNECTION_INFO['PORT'],
                         user=MYSQL_CONNECTION_INFO['USER'],
                         password=MYSQL_CONNECTION_INFO['PASSWORD'],
                         db=MYSQL_CONNECTION_INFO['DB'],
                         charset=MYSQL_CONNECTION_INFO['CHARSET'],
                         cursorclass=cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            cluster_index = 0
            cluster_index_id_dic = {}

            for cluster_center in cluster_center_list:

                vector = ""

                for num in range(cluster_center.__len__()):

                    if num == 0:
                        vector += str(round(float(cluster_center[num]), constants.number_of_decimal))
                    else:
                        vector += ", "
                        vector += str(round(float(cluster_center[num]), constants.number_of_decimal))

                query = ("INSERT INTO cluster (vector, revision, cdate) "
                         "VALUES (%s, %s, %s)")

                args = (vector, str(revision_id), datetime.now())

                cursor.execute(query, args)

                cluster_id = cursor.lastrowid

                cluster_index_id_dic[cluster_index] = cluster_id

                cluster_index += 1

            connection.commit()

            for cluster_index in cluster_dic:

                for student_id in cluster_dic[cluster_index]:

                    query = ("INSERT INTO cluster_student (cluster_id, student_id, revision, cdate) "
                         "VALUES (%s, %s, %s, %s)")

                    args = (str(cluster_index_id_dic[cluster_index]), str(student_id), str(revision_id), datetime.now())

                    cursor.execute(query, args)

            connection.commit()

            end_date = revision_controller.get_revision_date(revision_id)

            start_date = end_date - timedelta(days=constants.target_date_length)

            # 결과가 나온 후이니 오답 카운팅
            #각 cluster에서 틀린 문제 cluster_incorrect에 insert
            for cluster_index in cluster_dic:

                cluster_incorrect_dic = {}

                for student_id in cluster_dic[cluster_index]:

                    cursor.execute("""SELECT question_id FROM student_incorrect WHERE student_id = %s and cdate <= %s and cdate >= %s """,
                                   (str(student_id), str(end_date), str(start_date)))

                    items = cursor.fetchall()

                    for question in items:
                        if cluster_incorrect_dic.__contains__(question['question_id']):
                            cluster_incorrect_dic[question['question_id']] += 1
                        else:
                            cluster_incorrect_dic[question['question_id']] = 1

                for question_id in cluster_incorrect_dic:

                    query = ("INSERT INTO cluster_incorrect (cluster_id, question_id, count, revision, cdate) "
                             "VALUES (%s, %s, %s, %s, %s)")

                    args = (str(cluster_index_id_dic[cluster_index]), str(question_id), str(cluster_incorrect_dic[question_id]), revision_id, datetime.now())

                    cursor.execute(query, args)

                connection.commit()

    finally:
        connection.close()

    return revision_id
