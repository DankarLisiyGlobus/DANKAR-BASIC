#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys

words = ["PRINT","INT","STR","LIST","LET","PRINTVAR","CLEAR","INPUT","END","LINES","TYPE","COMMAND","OPEN","READ","WRITE","CLOSE","ADD","SUB","DIV","MULT","JUMP","JUMPIF"]


filename = sys.argv[1]

class Compiler:
    def __init__(self, code:list):
        self.lines_code = code
    def compile(self):
        """Преобразует высокоуровневые конструкции в команды JUMP"""
        processed_lines = []
        i = 0

        # Очистка кода от пустых строк и комментариев
        clean_lines = []
        for line in self.lines_code:
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#") and not clean_line.isspace():
                clean_lines.append(clean_line)

        i = 0
        while i < len(clean_lines):
            line = clean_lines[i]

            # Проверяем IF условие (без THEN)
            if line.startswith("IF<<"):
                # Извлекаем условие после IF
                condition = line[4:].strip()  # Убираем "IF "

                # Извлекаем блок действий до ENDIF
                action_block = []
                i += 1
                while i < len(clean_lines) and clean_lines[i] != "ENDIF":
                    action_block.append(clean_lines[i])
                    i += 1

                # Вычисляем позицию конца IF
                end_position = len(processed_lines) + len(action_block) + 1

                # Генерируем команды JUMP
                processed_lines.append(f"JUMP_IF not {condition} >{end_position}")
                processed_lines.extend(action_block)
                processed_lines.append(f"# Конец IF")

                i += 1  # Пропускаем ENDIF

            # Проверяем FOR<<итерации
            elif line.startswith("FOR<<"):
                # Извлекаем количество итераций
                iterations_match = re.match(r'FOR<<(\d+)', line)
                if iterations_match:
                    iterations = iterations_match.group(1)
                else:
                    iterations = "0"

                # Извлекаем блок цикла до ENDFOR
                loop_block = []
                i += 1
                while i < len(clean_lines) and clean_lines[i] != "ENDFOR":
                    loop_block.append(clean_lines[i])
                    i += 1

                # Вычисляем позиции для прыжков
                loop_start = len(processed_lines) + 4
                loop_end = len(processed_lines) + len(loop_block) + 5

                # Генерируем команды цикла
                processed_lines.extend([
                    f"# Начало цикла FOR<<{iterations}",
                    f"INT i 0",
                    f"INT max {iterations}",
                    f"# Метка начала цикла",
                    f"#FOR-START",
                ])

                # Тело цикла
                processed_lines.extend(loop_block)

                # Инкремент и прыжок назад
                processed_lines.extend([
                    f"ADD i 1",
                    f"JUMP_IF not @i == @max >{loop_start}",
                    f"# Конец цикла FOR"
                ])

                i += 1  # Пропускаем ENDFOR

            else:
                processed_lines.append(line)
                i += 1

        return processed_lines

    def save_compiled(self, output_filename):
        """Сохраняет скомпилированный код в файл"""
        with open(output_filename, "w", encoding="utf-8") as f:
            for line in self.compiled_code:
                f.write(line + "\n")
        print(f"Скомпилированный код сохранен в: {output_filename}")

    def print_compiled(self):
        """Выводит скомпилированный код"""
        print("\n" + "=" * 50)
        print("СКОМПИЛИРОВАННЫЙ КОД:")
        print("=" * 50)
        for i, line in enumerate(self.compiled_code):
            print(f"{i:3}: {line}")

class basic:
    def __init__(self,filename):
        self.filename = filename
        self.opened_file = open(filename,"r",encoding="utf-8")
        self.code = self.opened_file.read()
        self.lines_code = self.code.split("\n")
        compiler_ = Compiler(self.lines_code)
        self.lines_code = compiler_.compile()

        self.functions  = {}

        self.variables = {"__name__": filename,"i":0}

        self.run = True
        self.current_line = 0

        self.jumping = False

        try:
            while self.run:
                self.jumping = False
                if self.current_line+1 == len(self.lines_code):
                    self.run = False
                    break
                line = self.lines_code[self.current_line]
                self.execute(line,self.current_line)
                if not self.jumping:
                    self.current_line += 1
        except IndexError as e:
            print("IndexError! Возможно ошибка компилятора/либо вы неправильно использовали JUMP/JUMP_IF")
            print(self.current_line)
            #print(self.lines_code)


        #print("Программа успешно выполнена, код 0")
        #print("Для возврата нажмите Enter")
        #input()
        exit(0)

    def get_bool(self,expression:str):
        words = expression.split(" ")
        result = ""
        for word in words:
            if self.get_type(word) == "var":
                type_var = type(self.variables[word[1::]])
                if type_var == str:
                    result += "'"
                    result += str(self.variables[word[1::]])
                    result += "'"
                elif type_var == int:
                    result += str(self.variables[word[1::]])

                continue
            result += str(word)
            result += " "
        return bool(eval(result))
    def get_type(self,var:str):
        if var != "":
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
    def get_value(self,expression:str):
        if expression != "":
            if expression[0] == "'" and expression[-1] == "'":
                text = expression[1::]
                text = text[:-1]
                return str,text
            elif expression[0] == "#":
                return int,int(expression[1::])
            elif expression[0] == "@":
                try:
                    return "var",self.variables[expression[1::]]
                except:
                    print(f"Не обьявлена переменная {expression[1::]}")
                    exit(1)
            else:
                return None,None
        else:
            return None
    def execute(self,line:str,ii:int):
        #print(line)
        word = line.split(" ")[0]
        args = line.split(" ")[1::]
        text = ""
        word = word.upper()
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
            print(self.get_value(text)[1])
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
        elif word == "COMMAND":
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
        elif word == "JUMP":
            self.current_line = int(args[0])
            self.jumping = True
        elif word == "JUMP_IF":
            exspression = text.split(">")[0]
            line_number = int(text.split(">")[1])
            if self.get_bool(exspression):
                self.current_line = len(self.lines_code) if line_number > len(self.lines_code) else line_number
                #print(f"JUMP_IF to {len(self.lines_code) if line_number > len(self.lines_code) else line_number} self.current_line = {self.current_line}")
                self.jumping = True
        else:
            print(f"Неизвестное слово {word} ,строка {ii}")
            exit(1)


lang = basic(filename)


