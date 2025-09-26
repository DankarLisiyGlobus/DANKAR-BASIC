#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys


filename = sys.argv[1]
class basic:
    def __init__(self,filename):
        self.filename = filename
        self.opened_file = open(filename,"r",encoding="utf-8")
        self.code = self.opened_file.read()
        self.lines_code = self.code.split("\n")

        self.functions  = {}

        self.variables = {"__name__": filename,"i":0}


        for i,line in enumerate(self.lines_code):
            self.execute(line,i)

        print("Программа успешно выполнена, код 0")
        print("Для возврата нажмите Enter")
        input()
        exit(0)

    def get_bool(self,expression:str):
        words = expression.split(" ")
        result = ""
        for word in words:
            if self.get_type(word) == "var":
                result += str(self.variables[word[1::]])
                continue
            result += str(word)
        return bool(eval(result))
    def get_type(self,var:str):
        if var[0] == "'" and var[-1] == "'":
            return str
        elif var[0] == "#":
            return int
        elif var[0] == "[" and var[-1] == "]":
            return list
        elif var[0] == "@":
            return "var"
        else:
            return None
    def init_list(self,name,data:list):
        for i, element in enumerate(data):
            type = self.get_type(element)
            if type == str:
                text = element[1::]
                text = text[:-1]
                data[i] = str(text)
                continue
            elif type == int:
                data[i] = int(element)
                continue
        self.variables[name] = data
    def execute(self,line:str,ii:int):
        #try:
            word = line.split(" ")[0]
            args = line.split(" ")
            args = args[1::]
            text = ""
            for i in range(len(args)):
                text += args[i]
                if i+1 != len(args):
                    text += " "

            if word.isspace():
                return
            if word == "":
                return
            if word[0] == "#":
                return
            if word == "PRINT":
                print(text)
            elif word == "INT":
                self.variables[args[0]] = int(args[1])
            elif word == "STR":
                self.variables[args[0]] = str(args[1])
            elif word == "LIST":
                data = args[1::]
                self.init_list(args[0],data)
            elif word == "LET":
                var = ""
                arg2 = args[1::]
                for i,part in enumerate(arg2):
                    var += part
                    if i+1 != len(arg2):
                        var += " "
                typee = self.get_type(var)
                if typee == str:
                    text = var[1::]
                    text = text[:-1]
                    self.variables[args[0]] = str(text)
                elif typee == int:
                    var = var[1::]
                    self.variables[args[0]] = int(var)
                elif typee == list:
                    data = var[1::]
                    data = data[:-1]
                    data = data.split(",")
                    self.init_list(args[0],data)
                elif typee == None:
                    self.variables[args[0]] = None
            elif word == "PRINTVAR":
                print(self.variables[args[0]])
            elif word == "CLEAR":
                os.system("clear")
            elif word == "INPUT":
                self.variables[args[0]] = str(input(args[1]))
            elif word == "END":
                print("Программа успешно выполнена, код 0")
                exit(0)
            elif word == "LINES":
                self.variables[args[0]] = self.variables["LINES"]
            elif word == "TYPE":
                self.variables[args[1]] = str(type(self.variables[args[0]]))
            elif word == "SYSTEM":
                os.system(text)
            elif word == "OPEN":
                self.opened_file = open(args[0],args[1],encoding=args[2])
            elif word == "READ":
                self.variables[args[0]] = self.opened_file.read()
            elif word == "WRITE":
                self.opened_file.write(self.variables[args[0]])
            elif word == "CLOSE":
                self.opened_file.close()
                self.opened_file = open(self.filename,"r",encoding="utf-8")
            elif word == "IF":
                expression = line.split("/")[1]
                expression_bool = self.get_bool(expression)
                actions = line.split(":")[1]
                actions_lines = actions.split(",")
                if expression_bool:
                    for action in actions_lines:
                        self.execute(action,ii)
            elif word == "FOR":
                i = line.split("|")[1]
                i = eval(i)
                actions = line.split(":")[1]
                actions_lines = actions.split(";")
                for i in range(i):
                    for action in actions_lines:
                        self.execute(action,ii)
                        self.variables["i"] += 1
                self.variables["i"] = 0
                self.variables["i"] = 0
            elif word == "ADD":
                self.variables[args[0]] += int(args[1])
            elif word == "SUB":
                self.variables[args[0]] -= int(args[1])
            elif word == "MULT":
                res = self.variables[args[0]] * int(args[1])
                self.variables[args[0]] = res
            elif word == "DIV":
                res = self.variables[args[0]] // int(args[1])
                self.variables[args[0]] = res
            elif word == "DEF":
                name = line.split("<")[1]
                name = name.split(">")[0]
                actions = line.split("::")[1]
                actions_lines = actions.split(";;")
                self.functions[name] = actions_lines
            elif word == "CALL":
                for action in self.functions[args[0]]:
                    self.execute(action,ii)
            else:
                print(f"Неизвестное слово {word} ,строка {ii}")
                exit(1)

        #except Exception as e:
        #    print(f"Ошибка {e} ,строка {ii}")
        #    exit(1)

lang = basic(filename)


