from pprint import pprint
import psycopg2
import sqlalchemy as sql
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from modules.logger import logger
from modules.files import read_csv_file


DICT_PATH = 'data/rus_eng_dict.csv'
LOG_PATH = 'data/main.log'


class English_DB:
    def __init__(self, db_user=None, db_password=None):
        self._db_name = 'eng_rus_bot_db'
        self._DSN = 'postgresql://{}:{}@localhost:5432/{}'.format(
            db_user, db_password, self._db_name)

        if db_user and db_password:
            self._engine = sql.create_engine(self._DSN)
            _Session = sessionmaker(bind=self._engine)
            self._session = _Session()

            self._integrity_check()
    
    def get_user_words(self, telegram_id):
        user_id = self.get_user_id(telegram_id)

        main_words = self.get_main_words()
        stop_words = self.get_stop_words(user_id)
        extra_words = self.get_extra_words(user_id)        
        
        main_words = [(line.rus_word, line.eng_translation)
                      for line in main_words]
        if extra_words:
            main_words.extend([(line.rus_word, line.eng_translation)
                               for line in extra_words])
        if stop_words:
            main_words = set(main_words) - set([(line.rus_word, line.eng_translation)
                                                 for line in stop_words])
        
        return tuple(main_words)

    def get_main_words(self):
        '''Returns all words in main dictionary.
        Added by users words not included'''
        return self._session.query(main_dictionary).all()
    
    def get_extra_words(self, user_id):
        '''Returns words that user has added.\n
        For user_id takes user's id in database, not telegram id'''
        return self._session.query(extra_dictionary).join(
            extra_user_words,
            extra_dictionary.extra_ID == extra_user_words.extra_ID).filter(
                extra_user_words.user_ID == user_id).all()
    
    def get_stop_words(self, user_id):
        '''Returns user's stop words.\n
        For user_id takes user's id in database, not telegram id'''
        return self._session.query(main_dictionary).join(
            stop_user_words).filter(
                stop_user_words.user_ID == user_id).all()        

    @logger(LOG_PATH)
    def add_user(self, telegram_id):
        '''Adds new user to database by telegram id'''
        self._session.add(users(telegram_ID=telegram_id))
        self._session.commit()
    
    @logger(LOG_PATH)
    def delete_user(self, telegram_id):
        '''Deletes user from database by telegram id'''
        self._session.query(users).filter(
            users.telegram_ID == telegram_id).delete()
        self._session.commit()

    @logger(LOG_PATH)
    def add_extra_word(self, telegram_id, word, translate):
        '''Adds new word to extra dictionary in database
        if it's not existing in main dictionary. In case
        of success returns True'''
        word = word.lower()
        translate = translate.lower()
        if self.find_object(main_dictionary, main_dictionary.rus_word == word):
            return 'WordExists'
        
        if not self.find_object(extra_dictionary, extra_dictionary.rus_word == word):
            self._session.add(extra_dictionary(rus_word=word,
                                            eng_translation=translate))
            
        extra_ID = self.find_object(extra_dictionary,
                               extra_dictionary.rus_word == word)[0].extra_ID
        user_ID = self.find_object(
            users, users.telegram_ID == telegram_id)[0].user_ID
        self._session.add(extra_user_words(user_ID=user_ID,
                                           extra_ID=extra_ID))
        try:
            self._session.commit()
            return True
        except sql.exc.IntegrityError:
            self._session.rollback()
            return 'UserToWordExists'
    
    @logger(LOG_PATH)
    def add_stop_word(self, telegram_id, word):
        '''Adds word to stop words list for user.
        If the word is in extra dictionary, just the user-word
        relation will be removed'''
        user_id = self.get_user_id(telegram_id)
        word_id = self.find_object(
            main_dictionary, main_dictionary.rus_word == word)
        if word_id:
            self._session.add(stop_user_words(user_ID=user_id,
                                            main_ID=word_id[0].main_ID))
            self._session.commit()
        else:
            # In case the word that user wants to remove is added
            word_id = self.find_object(
                extra_dictionary, extra_dictionary.rus_word == word)
            if word_id:
                self._remove_userword_relation(user_id, word_id[0].extra_ID)
            else:
                return 'WordDoesNotExist'
    
    def get_user_id(self, telegram_id):
        user_data = self.find_object(users, users.telegram_ID == telegram_id)
        if user_data:
            return user_data[0].user_ID
        else:
            return 'UserDoesNotExist'
    
    def find_object(self, table_name, expression):
        return self._session.query(table_name).filter(expression).all()

    def test_connection(self, db_user, db_password):
        try:
            with psycopg2.connect(database=self._db_name,
                                user=db_user,
                                password=db_password) as connection:
                pass
        except psycopg2.OperationalError as error:
            self._session.rollback()
            if 'does not exist' in str(error):
                return 'NotExists'
            elif 'password authentication failed' in str(error):
                return 'WrongUserInfo'
            else:
                raise

        return 'Exists'
    
    def _remove_userword_relation(self, user_id, extra_id):
        self._session.query(extra_user_words).filter(
            extra_user_words.user_ID == user_id).filter(
                extra_user_words.extra_ID == extra_id).delete()
        self._session.commit()
    
    def _integrity_check(self):
        create_tables(self._engine)
        self._fill_db()

    def _fill_db(self):
        if self._is_table_empty(main_dictionary):
            dictionary = read_csv_file(DICT_PATH)
            for line in dictionary:
                self._session.add(
                    main_dictionary(rus_word=line['word'],
                                    eng_translation=line['translate']))
            self._session.commit()

    def _is_table_empty(self, table_name):
        count = self._session.query(table_name).count()
        return not count


Base = declarative_base()


class users(Base):
    __tablename__ = "users"
    
    user_ID = sql.Column(sql.Integer, primary_key=True)
    telegram_ID = sql.Column(sql.String, unique=True, nullable=False)


class main_dictionary(Base):
    __tablename__ = "main_dictionary"
    
    main_ID = sql.Column(sql.Integer, primary_key=True)
    rus_word = sql.Column(sql.String, unique=True, nullable=False)
    eng_translation = sql.Column(sql.String, nullable=False)

    stop_user_words = relationship("stop_user_words", 
                                   backref="main_dictionary")


class extra_dictionary(Base):
    __tablename__ = "extra_dictionary"
    
    extra_ID = sql.Column(sql.Integer, primary_key=True)
    rus_word = sql.Column(sql.String, unique=True, nullable=False)
    eng_translation = sql.Column(sql.String, nullable=False)

    extra_user_words = relationship("extra_user_words",
                                    backref="extra_dictionary")


class stop_user_words(Base):
    __tablename__ = "stop_user_words"

    stop_word_ID = sql.Column(sql.Integer, unique=True, primary_key=True)
    user_ID = sql.Column(sql.Integer, sql.ForeignKey("users.user_ID"),
                         nullable=False)
    main_ID = sql.Column(sql.Integer, sql.ForeignKey("main_dictionary.main_ID"),
                         nullable=False)
    
    user = relationship("users", backref="stop_user_words")

    __table_args__ = (
        sql.UniqueConstraint('user_ID', 'main_ID'),
    )
    

class extra_user_words(Base):
    __tablename__ = "extra_user_words"

    extra_word_ID = sql.Column(sql.Integer, unique=True, primary_key=True)
    user_ID = sql.Column(sql.Integer, sql.ForeignKey("users.user_ID"),
                         nullable=False)
    extra_ID = sql.Column(sql.Integer, sql.ForeignKey("extra_dictionary.extra_ID"),
                          nullable=False)
    
    user = relationship("users", backref="extra_user_words")

    __table_args__ = (
        sql.UniqueConstraint('user_ID', 'extra_ID'),
    )


def create_tables(engine):
    Base.metadata.create_all(engine)