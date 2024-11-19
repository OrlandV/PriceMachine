import os
import csv
import json
from tkinter import filedialog


class PriceMachine:
    
    def __init__(self):
        self.data = []  # Список строк таблицы с данными.
        self.result = ''  # Текст (строка) для вывода в консоль.
        self.name_length = {'Наименование': 12, 'Цена': 4, 'Вес': 3, 'Файл': 4, 'Цена за кг': 10}  # Длины строк-ячеек.

    def _wipe_name_length(self):
        """
        Сброс длин строк-ячеек перед построением новой таблицы для консоли.
        """
        self.name_length = {'Наименование': 12, 'Цена': 4, 'Вес': 3, 'Файл': 4, 'Цена за кг': 10}

    def _set_name_length(self, row: dict):
        """
        Установка новых длин строк-ячеек, если в новой строке таблицы они больше ранее установленных.
        :param row: Строка таблицы, ячейки которой будут сравниваться с ранее установленными длинами.
        """
        for key, item in row.items():
            if key == 'Цена за кг':
                x = len(f'{item:.1f}')
                if self.name_length[key] < x:
                    self.name_length[key] = x
            elif self.name_length[key] < len(item):
                self.name_length[key] = len(item)

    def _set_result(self, data: list[dict]):
        """
        Формирование текста для вывода в консоль.
        :param data: Данные для вывода.
        """
        # Заголовки столбцов таблицы.
        al = ('<', '>', '>', '^', '^')  # Направления выравнивания.
        self.result = '{:<5}'.format('№')
        i = 0
        for key, item in self.name_length.items():
            self.result += f' {key:{al[i]}{item}}'
            i += 1
        # Данные.
        for number, item in enumerate(data):
            self.result += (f'\n{number + 1:<5} {item['Наименование']:<{self.name_length['Наименование']}}'
                            f' {item['Цена']:>{self.name_length['Цена']}} {item['Вес']:>{self.name_length['Вес']}}'
                            f' {item['Файл']:^{self.name_length['Файл']}}'
                            f' {item['Цена за кг']:^{self.name_length['Цена за кг']}.1f}')

    def load_prices(self, file_path='') -> str:
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        Допустимые названия для столбца с товаром:
            товар
            название
            наименование
            продукт
        Допустимые названия для столбца с ценой:
            розница
            цена
        Допустимые названия для столбца с весом (в кг):
            вес
            масса
            фасовка
        :param file_path: Путь к папке с прайсами.
        """
        product_headers = {'товар', 'название', 'наименование', 'продукт'}
        price_headers = {'розница', 'цена'}
        weight_headers = {'вес', 'масса', 'фасовка'}
        files = os.listdir(file_path)
        prices = ''  # Строка-список найденных прайсов.
        for file_name in files:
            if 'price' in file_name and os.path.isfile(f'{file_path}/{file_name}'):
                prices += '\n' + file_name
                with open(file_name, 'r', encoding='utf8') as file:
                    csv_reader = csv.DictReader(file)  # Чтение CSV как словаря.
                    csv_list = []  # Список-контейнер для словарей-строк.
                    for row in csv_reader:
                        csv_list.append(row)
                # Словарь соответствия заголовков столбцов результирующей таблицы заголовкам в текущем файле.
                current_headers = {}
                for product in product_headers:
                    if product in csv_list[0]:
                        current_headers['Наименование'] = product
                        break
                for price in price_headers:
                    if price in csv_list[0]:
                        current_headers['Цена'] = price
                        break
                for weight in weight_headers:
                    if weight in csv_list[0]:
                        current_headers['Вес'] = weight
                        break
                # Наполнение результирующей таблицы.
                for row in csv_list:
                    self.data.append({
                        'Наименование': row[current_headers['Наименование']],
                        'Цена': row[current_headers['Цена']],
                        'Вес': row[current_headers['Вес']],
                        'Файл': file_name,
                        'Цена за кг': int(row[current_headers['Цена']]) / int(row[current_headers['Вес']])
                    })
                    self._set_name_length(self.data[len(self.data) - 1])  # Установка длин строк-ячеек.
        if self.data:
            self.data = sorted(self.data, key=lambda d: d['Цена за кг'])  # Сортировка.
            self._set_result(self.data)  # Формирование текста для вывода в консоль.
        if len(prices) > 0:
            print(f'Загружены прайсы:{prices}\n')
        else:
            print('Прайсы не найдены.')
        return self.result

    # Как позже понял, подразумевалось использовать список кортежей, для которых нужна функция согласования
    # заголовков столбцов и индексов в кортеже. Если использовать список словарей, то эта функция не нужна.
    # def _search_product_price_weight(self, headers):
    #     '''
    #         Возвращает номера столбцов
    #     '''
    #     pass

    def export_to_html(self, fname='output.html') -> str:
        """
        Экспорт данных в HTML-файл.
        :param fname: Путь к файлу. По умолчанию — "output.html".
        :return: Сообщение о сохранении в файл.
        """
        result = '''<!DOCTYPE html>
<html>
<head>
    <title>Позиции продуктов</title>
</head>
<body>
    <table>
        <tr>
            <th>Номер</th>
            <th>Наименование</th>
            <th>Цена</th>
            <th>Вес</th>
            <th>Файл</th>
            <th>Цена за кг</th>
        </tr>'''
        for number, item in enumerate(self.data):
            result += f'''
        <tr>
            <td>{number + 1}</td>
            <td>{item['Наименование']}</td>
            <td>{item['Цена']}</td>
            <td>{item['Вес']}</td>
            <td>{item['Файл']}</td>
            <td>{item['Цена за кг']:.1f}</td>
        </tr>'''
        result += '\n\t</table>\n</body>'
        with open(fname, 'w', encoding='utf8') as file:
            file.write(result)
        return f'Вся таблица сохранена в файле «{fname}».'
    
    def find_text(self, text: str) -> str:
        """
        Поиск строк по фрагменту наименования товара и вывод результата.
        :param text: Фрагмент наименования товара.
        :return: Текст с результатом поиска для вывода в консоль.
        """
        self._wipe_name_length()
        data = []  # Будущий результат поиска.
        for row in self.data:
            if text in row['Наименование'].lower():
                data.append(row)
                self._set_name_length(row)
        self._set_result(data)
        return self.result

    def export_to_csv(self, fname='output.csv') -> str:
        """
        Экспорт данных в CSV-файл.
        :param fname: Путь к файлу. По умолчанию — "output.csv".
        :return: Сообщение о сохранении в файл.
        """
        with open(fname, 'w', encoding='utf8') as file:
            csv_writer = csv.writer(file, lineterminator='\n')
            csv_writer.writerow(('№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг'))
            for number, item in enumerate(self.data):
                csv_writer.writerow((number + 1, item['Наименование'], item['Цена'], item['Вес'], item['Файл'],
                                     item['Цена за кг']))
        return f'Вся таблица сохранена в файле «{fname}».'

    def export_to_json(self, fname='output.json') -> str:
        """
        Экспорт данных в JSON-файл.
        :param fname: Путь к файлу. По умолчанию — "output.json".
        :return: Сообщение о сохранении в файл.
        """
        with open(fname, 'w', encoding='utf8') as file:
            json.dump(self.data, file)
        return f'Вся таблица сохранена в файле «{fname}».'


if __name__ == '__main__':
    pm = PriceMachine()
    # Диалоговое окно выбора папки с прайсами вместо ввода пути в коде или консоли.
    print(pm.load_prices(filedialog.askdirectory(
        initialdir='..',
        mustexist=True,
        title='Выбор пути к папке с прайсами'
    )))
    print()
    while True:
        print('Для фильтрации укажите фрагмент наименования товара.')
        print('Для экспорта данных в файл введите соответственно "html", "csv" или "json".')
        print('Для завершения работы программы введите слово "exit".')
        print('Перед завершением все данные сохраняться в HTML-файл "output.html".\n')
        text = input('Введите искомый фрагмент или команду: ').lower()
        if text == 'exit':
            break
        elif text == 'html':
            # Диалоговое окно выбора HTML-документа для сохранения вместо ввода пути в коде или консоли.
            print(pm.export_to_html(filedialog.asksaveasfilename(
                defaultextension='.html',
                filetypes=(('HTML-документ', '*.html'),),
                initialdir='.',
                initialfile='output.html',
                title='Выбор HTML-документа для сохранения'
            )))
        elif text == 'csv':
            # Диалоговое окно выбора CSV-документа для сохранения вместо ввода пути в коде или консоли.
            print(pm.export_to_csv(filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=(('CSV-документ', '*.csv'),),
                initialdir='.',
                initialfile='output.csv',
                title='Выбор CSV-документа для сохранения'
            )))
        elif text == 'json':
            # Диалоговое окно выбора JSON-документа для сохранения вместо ввода пути в коде или консоли.
            print(pm.export_to_json(filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=(('JSON-документ', '*.json'),),
                initialdir='.',
                initialfile='output.json',
                title='Выбор JSON-документа для сохранения'
            )))
        else:
            # Поиск товара по фрагменту наименования.
            print(pm.find_text(text))
        print()
    print(pm.export_to_html())  # Сохранение в HTML-документ при завершении программы.
    print('Конец')
