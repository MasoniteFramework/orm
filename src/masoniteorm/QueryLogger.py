import logging

class QueryLogger:

    logger = None
    
    logger_message = "%{asctime} - {module} - {process} - {thread} - {levelname} - {message}"
    query_message = "{query}, {bindings}. Executed in {query_time}ms"

    @classmethod
    def configure(cls, handlers, msg_formatter=None):
        
        cls.logger = logging.getLogger('masoniteorm.connection.queries')

        msg_logger = msg_formatter if msg_formatter else cls.logger_message
            
        logger_msg_formatter = logging.Formatter(msg_logger)

        for handler in handlers:
            handler.setFormatter(logger_msg_formatter)
            handler.setLevel(logging.INFO)
            cls.logger.addHandler(handler)
        
        
    @classmethod
    def info(cls, message, extra_info=None):

        message = message + cls.query_message if extra_info else message
        print(cls.logger)
        # print(help(cls.logger))

        if extra_info:

            query_time = extra_info.get('query_time', None)
            
            if query_time:
                formatted = "{:.2f}".format(query_time)
                extra_info.update({"query_time": query_time})

            cls.logger.log(message, {"extra":extra_info})
        cls.logger.log(message)
