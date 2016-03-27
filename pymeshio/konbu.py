class ParseContext:
    def __init__(self, data, position=0):
        self.data=data
        self.position=position

    def __str__(self):
        return "{position}/{length}".format(
                position=self.position, length=len(self.data))

    def is_end(self):
        return self.position>=len(self.data)

    def get(self):
        if self.is_end():
            raise Exception("no more data")
        else:
            return self.data[self.position]

    def advance(self):
        return ParseContext(self.data, self.position+1)

class Result:
    def __init__(self, value, position: ParseContext, is_success: bool):
        self.value=value
        assert position!=None, "no position"
        self.position=position
        self.is_success=is_success

    def __str__(self):
        return "{0}:{1} => {2}".format(
                self.position, 
                "succenss" if self.is_success else "false", 
                self.value)

def value_of(target):
    def parser(i):
        value=i.get()
        if value==target:
            return Result(target, i.advance(), True);
        else:
            return Result(None, i, False);
    return parser

def ascii_of(target):
    def parser(i):
        current=i
        for x in target:
            value=current.get()
            if value!=x:
                return Result(None, i, False);
            current=current.advance()
        return Result(target, current, True)
    return parser

def parser_builder(generator):
    def parser(position):
        it=generator()
        last_result=Result(None, position, True)
        try:
            while True:
                current_parser=it.send(last_result.value)
                result=current_parser(last_result.position)
                if result.is_success:
                    # next
                    last_result=result
                else:
                    # false
                    return result
        except StopIteration as ex:
            # success
            if ex.value:
                return Result(ex.value, last_result.position, True)
            else:
                return last_result
        except Exception as ex:
            # exception
            return Result(ex, last_result.position, False)
    return parser


if __name__=="__main__":
    @parser_builder
    def sub_parser():
        x = yield value_of(1)
        y = yield value_of(2)
        z = yield value_of(3)
        return (x, y, z)

    @parser_builder
    def root_parser():
        _123 = yield sub_parser
        x = yield value_of(4)
        return (*_123, x)
        
    print(root_parser(ParseContext([1, 2, 3, 4])))

