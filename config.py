import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgres://yyigglgedkjamf:4005d027222aea85a71ecf05179657a00c092ebf39ac3af7207fc03e07456d39@ec2-107-21-248-200.compute-1.amazonaws.com:5432/d68q1rlffi76s9'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
