import json
import sqlite3


# 读取json文件 并转化为 字典
jsonFileName = './in.json'
with open(jsonFileName,encoding='utf-8-sig') as jsonFile:
    jsonStr = jsonFile.readlines()
questionDict = json.loads(jsonStr[0])
questionList = questionDict['data']['userPagerQuestionList']



conn = sqlite3.connect(u'安全考试.db')
c = conn.cursor()

# 创建视图
c.execute("""CREATE VIEW IF NOT EXISTS DAAN AS
        SELECT
            CASE 
                WHEN q.type = '1' THEN '单选题' 
                WHEN q.type = '2' THEN '多选题' 
                WHEN q.type = '3' THEN '判断题' 
                ELSE '不祥' 
            END AS "题型",
            
            q.title AS "问题",
            
            CASE 
                WHEN q.rightflag = '1' AND q.type = '3' AND q.useranswer = '0' THEN 'B. 错误' 
                WHEN q.rightflag = '1' AND q.type = '3' AND q.useranswer = '1' THEN 'A. 正确' 
                WHEN q.rightflag = '1' AND q.type = '1' THEN 
                    (SELECT
                        GROUP_CONCAT(char( 65 + a.sort )|| '. ' || a.content,' ')
                    FROM
                        answer_option_list a
                    WHERE
                        a.qid = q.id 
                    )
                WHEN q.rightflag = '1' AND q.type = '2' THEN 
                    (SELECT
                        GROUP_CONCAT(char ( 65 + a.sort )|| '. ' || a.content,' ')
                    FROM
                        answer_option_list a
                    WHERE
                        a.qid = q.id 
                    )
                ELSE '赞无答案' 
            END AS "正确答案",
            
            CASE WHEN q.type = '3' THEN 'A. 正确 B. 错误' 
                 ELSE GROUP_CONCAT(char ( 65 + a.sort )|| '. ' || a.content,' ')
            END AS "选项"
            
        FROM
            question_list q 
            
        LEFT JOIN 
            question_option_list a ON q.id = a.qid
        
        GROUP BY
            q.title

        """)




c.execute('''CREATE TABLE IF NOT EXISTS question_list
       (id  TEXT PRIMARY KEY  NOT NULL unique,
       useranswer  TEXT,
       useranswerimage  TEXT,
       userscore  TEXT,
       userscorestr  TEXT,
       rightflag  TEXT,
       sort  TEXT,
       score TEXT,
       type TEXT,
       title TEXT,
       answer TEXT,
       analysis TEXT,
       annotate TEXT
       );''')

c.execute('''CREATE TABLE IF NOT EXISTS question_option_list
       (qid TEXT NOT NULL,
       aid TEXT NOT NULL,
       content TEXT,
       sort  TEXT
       );
       ''')
c.execute("CREATE UNIQUE INDEX IF NOT EXISTS question_option_unique ON question_option_list(qid, aid);")

c.execute('''CREATE TABLE IF NOT EXISTS answer_option_list
       (qid TEXT NOT NULL,
       aid TEXT NOT NULL,
       content TEXT,
       sort  TEXT
        );
       ''')
c.execute("CREATE UNIQUE INDEX IF NOT EXISTS answer_option_unique ON answer_option_list(qid, aid);")
conn.commit()


print("Table created successfully")




cursor = c.execute("select * from question_list where rightflag = '0'")
wrongflag = [row[0] for row in cursor]


for question in questionList:
    if question['id'] in wrongflag and question['rightFlag']=='1':      # 如果问题id 在已存在的数据库中的答案是错的,并且新的答案是正确的,那么替换已存在的记录
        c.execute("INSERT OR REPLACE INTO question_list (id,useranswer,useranswerimage,userscore,userscorestr,rightflag, \
               sort,score,type,title,answer,analysis,annotate)  \
               VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(question['id']), str(question['userAnswer']),
                          str(question['userAnswerImage']), str(question['userScore']),
                          str(question['userScoreStr']), str(question['rightFlag']),
                          str(question['sort']), str(question['score']),
                          str(question['type']), str(question['title']),
                          str(question['answer']), str(question['analysis']),
                          str(question['annotate']) )
                )
    else:
        c.execute("INSERT OR IGNORE INTO question_list (id,useranswer,useranswerimage,userscore,userscorestr,rightflag, \
                   sort,score,type,title,answer,analysis,annotate)  \
                   VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(question['id']), str(question['userAnswer']),
                              str(question['userAnswerImage']), str(question['userScore']),
                              str(question['userScoreStr']), str(question['rightFlag']),
                              str(question['sort']), str(question['score']),
                              str(question['type']), str(question['title']),
                              str(question['answer']), str(question['analysis']),
                              str(question['annotate']) )
                 )
        for questionOption in  question['questionOptionList']:
            c.execute("""INSERT OR IGNORE INTO question_option_list (qid,aid,content,sort) VALUES ('{}','{}','{}','{}')
                      """.format(str(question['id']), str(questionOption['id']), str(questionOption['content']), str(questionOption['sort'])))

            if str(questionOption['id']) in  question['userAnswer'].split(','):
                c.execute("""INSERT OR IGNORE INTO answer_option_list (qid,aid,content,sort) VALUES ('{}','{}','{}','{}')
                          """.format(str(question['id']), str(questionOption['id']), str(questionOption['content']),str(questionOption['sort'])))

        if question['type']=='3':
            if question['userAnswer']== '1':
                answer = '正确'
                sort = '0'
            else :
                answer = '错误'
                sort = '1'

            c.execute("""INSERT OR IGNORE INTO answer_option_list (qid,aid,content,sort) VALUES ('{}','{}','{}','{}')
                      """.format(str(question['id']), "", answer, sort))

conn.commit()
conn.close()
