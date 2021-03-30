import pandas as pd
import numpy as np
import re
import time
import sys


degree = {
    "06": ("Академический бакалавр", "Специалист"),
    "07": ("Магистр",)
}
uni_module = {
    "0": "универсальный модуль",
    "1": "модуль философия мышление",
    "2": "модуль цифровая культура",
    "3": "модуль дизайн мышление",
    "4": "модуль предпринимательская культура",
    "5": "модуль soft skills",
    "6": "огнп",
    "7": "физическая культура",
    "8": "цифровая культура в профессиональной деятельности",
    "9": "общеуниверситетская дисциплина мировоззренческого модуля",
    "10": "иностранный язык",
    "11": "элективная дисциплина soft skills",
    "12": "факультативные дисциплины",
    "13": "общеуниверситетский модуль",
    "14": "иностранный язык в профессиональной деятельности",
    "15": "история",
    "16": "университетский фундаментальный модуль"
}
ognp_module = {
    "0": "математический модуль",
    "1": "естественнонаучный модуль",
    "2": "общепрофессиональный модуль",
    "3": "элективный модуль по группе направлений",
    "4": "межпрофильный модуль факультета",
    "5": "профильный профессиональный модуль",
    # "6": "специализац",
    "7": "факультетский модуль",
    "8": "цифровая культура в предметной области мегафакультета",
    "9": "профессиональный модуль",
    "10": "практика",
    "11": "гиа",
    "12": "фундаментальный модуль по огнп",
    "13": "неизвестный модуль"
}
"""
ognp_codes = {
    "1": ["12.03.04", "14.03.01", "16.03.03", "18.03.02", "19.03.01", "19.03.02", "19.03.03", "16.04.03", "18.04.02", "19.04.01", "19.04.02", "19.04.03", "20.04.01", "27.04.01"],
    "2": ["12.03.01", "13.03.02", "15.03.04", "15.03.06", "24.03.02", "27.03.04", "11.04.03", "12.04.01", "13.04.02", "15.04.02", "15.04.04", "15.04.06", "23.04.03", "24.04.01", "24.04.02", "27.04.03"],
    "3": ["09.03.01", "09.03.04", "10.03.01", "11.03.03", "23.03.03", "44.03.04", "09.04.01", "09.04.04", "10.04.01", "27.04.04"],
    "4": ["27.03.05", "38.03.05", "27.04.02", "27.04.05", "27.04.08", "38.04.01", "38.04.05"],
    "5": ["01.03.02", "09.03.02", "01.04.02", "02.04.03", "09.04.02"],
    "6": ["09.03.03", "11.03.02", "45.03.04", "07.04.04", "09.04.03", "11.04.02", "27.04.07", "45.04.04"],
    "7": ["12.03.02", "12.03.03", "12.03.05", "12.05.01", "16.03.01", "12.04.02", "12.04.03", "12.04.04", "12.04.05", "16.04.01"]
}
"""


# remove multiple spaces and punctuation
def cleanText(text):
    cleaned = re.sub(r'[^\w\s]', ' ', text)
    cleaned = re.sub(' +', ' ', cleaned)
    cleaned = cleaned.replace('\xa0', '')
    cleaned = cleaned.replace('\t', '')
    cleaned = cleaned.strip()
    return cleaned


# calculate positions 1-3
def getPos123(xlsx_degree, xlsx_comp, xlsx_ognp, line=""):
    list_of_degrees = [d for d in degree if xlsx_degree in degree[d]]
    if not list_of_degrees: sys.exit("Неизвестный уровень образования в %sзаписи." % line)
    else: p1 = list_of_degrees[0]
    uni = ["6" if re.match("модуль внутривуз", xlsx_comp, flags=re.IGNORECASE) else
           "14" if xlsx_comp == "иностранный язык в профессиональной деятельности" else
           "10" if xlsx_comp == "иностранный язык" else
           u if re.match(uni_module[u], xlsx_comp, flags=re.IGNORECASE) else
           np.nan for u in uni_module]
    uni = [u for u in uni if str(u) != "nan"]
    module = ["5" if re.match("модуль [0-9]", xlsx_comp, flags=re.IGNORECASE) else
              "6" if re.search("специализац", xlsx_comp, flags=re.IGNORECASE) else
              p if re.match(ognp_module[p], xlsx_comp, flags=re.IGNORECASE) else
              np.nan for p in ognp_module]
    module = [m for m in module if str(m) != 'nan']
    if not uni and not module:
        sys.exit("Неизвестный модуль в %sзаписи." % line)
    if uni:
        return p1 + "." + "0" + "." + uni[0] + "."
    if module:
        return p1 + "." + str(xlsx_ognp) + "." + module[0] + "."
"""
ognp_num = ["3" if xlsx_sf_name == "Цифровые системы управления" else
            "2" if xlsx_sf_name == "Системы управления движением и навигации" else
            "1" if xlsx_sf_name == "Цифровые геотехнологии" else
            num if xlsx_sf_code in ognp_codes[num] else
            np.nan for num in ognp_codes]
ognp_num = [p for p in ognp_num if str(p) != 'nan']
if not ognp_num:
    print(xlsx_degree, xlsx_sf_code, xlsx_sf_name)
    sys.exit("Неизвестный шифр направления подготовки в %sзаписи." % line)
else: return p1 + "." + ognp_num[0] + "." + module[0] + "."
"""


# find max 4th value
def getMax4(dis_rep):
    list_of_4 = [int(dis_rep["DIS_CODE"][d].split(".")[3]) for d in dis_rep.index.values]
    if list_of_4: return max(list_of_4)
    else: return -1


def totalUnitInfo(data, sf_name, subj, comp, subj_code, cycle, year):
    credit_units = [0 for i in range(0, 12)]
    units = data.loc[(data["SUBFIELDNAME"] == sf_name) & (data["SUBJECT"] == subj) & (data["COMPONENT"] == comp) & (data["SUBJECT_CODE"] == subj_code) & (data["CYCLE"] == cycle) & (data["YEAR"] == year)]
    try:
        for u in units.index.values:
            if pd.isna(units["CREDITS"][u]) or units["CREDITS"][u] == 0 or units["CREDITS"][u] == ".":
                credit_units[int(units["SEMESTER"][u]) - 1] = "-"
            elif units["SEMESTER"][u] == ".":
                credit_units[11] = int(units["CREDITS"][u])
            else:
                credit_units[int(units["SEMESTER"][u]) - 1] = int(units["CREDITS"][u])
    except:
        pass
    return ",".join(map(str, credit_units))


def numUnitsCredits(units_credits):
    units = [u for u in units_credits.split(",") if u != "0"]
    int_creds = [0 if u == "-" else int(u) for u in units]
    return ",".join(map(str, [len(units), sum(int_creds)]))


def getPos4(rep, sem_xlsx, dis_code, subj, sf_name, lec, prac, lab, exam, pf, diff, cp, imp_id, lang):
    if subj not in rep["SUBJECT"].to_list():
        # print(1, end=" ")
        return str(getMax4(rep) + 1)
    else:
        rep1 = rep.loc[rep["SUBJECT"] == subj]
        new_sem_info = rep1["SEM_INFO"].apply(numUnitsCredits).to_list()
        rep3 = rep1.assign(UNITS_CREDITS=new_sem_info)
        if numUnitsCredits(sem_xlsx) not in new_sem_info:
            # print(2, end=" ")
            return str(getMax4(rep) + 1)
        else:
            rep2 = rep3.loc[rep3["UNITS_CREDITS"] == numUnitsCredits(sem_xlsx)].reset_index(drop=True)
            if lang not in rep2["LANGUAGE"].tolist() or imp_id not in rep2["IMPLEMENTOR_ID"].tolist():
                # print(3, end=" ")
                return str(getMax4(rep) + 1)
            else:
                rep4 = rep2.loc[(rep2["LANGUAGE"] == lang) | (rep2["IMPLEMENTOR_ID"] == imp_id)].reset_index(drop=True)
                # rows = len(rep4)
                var = 0
                for p in rep4.index.values:
                    if lec == rep4["LECTURE"][p] and lab == rep4["LAB"][p] and prac == rep4["PRACTICE"][p] and \
                            exam == rep4["EXAM"][p] and pf == rep4["PASS"][p] and diff == rep4["DIFF"][p] and cp == rep4["CP"][p]:
                        var += 1
                if var == 0:
                    # print(4, end=" ")
                    return str(getMax4(rep) + 1)
                else:
                    rep5 = rep4.loc[(rep4["LECTURE"] == lec)
                                    & (rep4["LAB"] == lab)
                                    & (rep4["PRACTICE"] == prac)
                                    & (rep4["EXAM"] == exam)
                                    & (rep4["PASS"] == pf)
                                    & (rep4["DIFF"] == diff)
                                    & (rep4["CP"] == cp)]
                    rows = len(rep5)
                    count = 0
                    for p in rep5.index.values:
                        if (rep5["SUBFIELDNAME"][p] != sf_name) and (dis_code.split(".")[2] in ("10", "11")) and (dis_code.split(".")[1] != "0"):
                            count += 1
                            if count != rows: continue
                            else:
                                print(5, end=" ")
                                return str(getMax4(rep) + 1)
                        else:
                            # print(6, end=" ")
                            return str(rep5["DIS_CODE"][p].split(".")[3])


# workaround for 01.04.02 Разработка программного обеспечения / Software Engineering
def softwareEngineering(rep, sem_xlsx, dis_code, subj, lec, prac, lab, exam, pf, diff, cp, imp_id, lang):
    p12 = dis_code[:-2]
    p3 = dis_code.split(".")[2]
    fin_rep = rep.loc[rep["DIS_CODE"].str.match(p12 + p3)]
    if subj not in rep["SUBJECT"].to_list():
        return p3 + "." + str(getMax4(fin_rep) + 1)
    else:
        rep1 = rep.loc[rep["SUBJECT"] == subj]
        new_sem_info = rep1["SEM_INFO"].apply(numUnitsCredits).to_list()
        rep2 = rep1.assign(UNITS_CREDITS=new_sem_info)
        if numUnitsCredits(sem_xlsx) not in new_sem_info:
            return p3 + "." + str(getMax4(fin_rep) + 1)
        else:
            rep3 = rep2.loc[rep2["UNITS_CREDITS"] == numUnitsCredits(sem_xlsx)].reset_index(drop=True)
            if lang not in rep3["LANGUAGE"].tolist() or imp_id not in rep3["IMPLEMENTOR_ID"].tolist():
                # print("e3", end=" ")
                return p3 + "." + str(getMax4(fin_rep) + 1)
            else:
                rep4 = rep3.loc[(rep3["LANGUAGE"] == lang) | (rep3["IMPLEMENTOR_ID"] == imp_id)].reset_index(drop=True)
                # rows = len(rep4)
                var = 0
                for p in rep4.index.values:
                    if lec == rep4["LECTURE"][p] and lab == rep4["LAB"][p] and prac == rep4["PRACTICE"][p] and \
                            exam == rep4["EXAM"][p] and pf == rep4["PASS"][p] and diff == rep4["DIFF"][p] and cp == \
                            rep4["CP"][p]:
                        var += 1
                if var == 0:
                    # print("e4", end=" ")
                    return p3 + "." + str(getMax4(fin_rep) + 1)
                else:
                    rep5 = rep4.loc[(rep4["LECTURE"] == lec)
                                    & (rep4["LAB"] == lab)
                                    & (rep4["PRACTICE"] == prac)
                                    & (rep4["EXAM"] == exam)
                                    & (rep4["PASS"] == pf)
                                    & (rep4["DIFF"] == diff)
                                    & (rep4["CP"] == cp)]
                    # rep5["DIS_CODE"] = rep5.groupby(["SUBJECT", "UNITS_CREDITS"])["DIS_CODE"].transform("first")
                    # print("e5", end=" ")
                    return ".".join(rep5.groupby(["SUBJECT", "UNITS_CREDITS"])["DIS_CODE"].transform("first")[0].split(".")[-2:])


# workaround for элективный модуль по группе направлений
def electiveModuleBachelor(rep, sem_xlsx, dis_code, subj, lec, prac, lab, exam, pf, diff, cp, imp_id, lang):
    p23 = ".".join(dis_code.split(".")[1:])
    fin_rep = rep.loc[rep["DIS_CODE"].str.match(dis_code)]
    if subj not in rep["SUBJECT"].to_list():
        # print("e1", str(getMax4(fin_rep) + 1))
        return p23 + str(getMax4(fin_rep) + 1)
    else:
        rep1 = rep.loc[rep["SUBJECT"] == subj]
        new_sem_info = rep1["SEM_INFO"].apply(numUnitsCredits).to_list()
        rep2 = rep1.assign(UNITS_CREDITS=new_sem_info)
        if numUnitsCredits(sem_xlsx) not in new_sem_info:
            # print("e2", str(getMax4(fin_rep) + 1))
            return p23 + str(getMax4(fin_rep) + 1)
        else:
            rep3 = rep2.loc[rep2["UNITS_CREDITS"] == numUnitsCredits(sem_xlsx)].reset_index(drop=True)
            if lang not in rep3["LANGUAGE"].tolist() or imp_id not in rep3["IMPLEMENTOR_ID"].tolist():
                # print("e3", end=" ")
                return p23 + str(getMax4(fin_rep) + 1)
            else:
                rep4 = rep3.loc[(rep3["LANGUAGE"] == lang) | (rep3["IMPLEMENTOR_ID"] == imp_id)].reset_index(drop=True)
                # rows = len(rep4)
                var = 0
                for p in rep4.index.values:
                    if lec == rep4["LECTURE"][p] and lab == rep4["LAB"][p] and prac == rep4["PRACTICE"][p] and \
                            exam == rep4["EXAM"][p] and pf == rep4["PASS"][p] and diff == rep4["DIFF"][p] and cp == \
                            rep4["CP"][p]:
                        var += 1
                if var == 0:
                    # print("e4", end=" ")
                    return p23 + str(getMax4(fin_rep) + 1)
                else:
                    rep5 = rep4.loc[(rep4["LECTURE"] == lec)
                                    & (rep4["LAB"] == lab)
                                    & (rep4["PRACTICE"] == prac)
                                    & (rep4["EXAM"] == exam)
                                    & (rep4["PASS"] == pf)
                                    & (rep4["DIFF"] == diff)
                                    & (rep4["CP"] == cp)]
                    # rep5["DIS_CODE"] = rep3.groupby(["SUBJECT", "UNITS_CREDITS"])["DIS_CODE"].transform("first")
                    # print("e5", end=" ")
                    return ".".join(rep3.groupby(["SUBJECT", "UNITS_CREDITS"])["DIS_CODE"].transform("first")[0].split(".")[1:])


def getPos5(data, new_sys_df):
    if new_sys_df == 1:
        data["VERSION"] = data.groupby(["DIS_CODE"])["VERSION"].transform("first")
    if new_sys_df == 0:
        data["VERSION"] = data.groupby(["DIS_CODE"])["VERSION"].transform("min")
    return data


# create sys_df if empty or does not exist
def create_sys_df():
    cols = ["EP_ID", "SUBJECT_CODE", "CYCLE", "MODULE_ID", "COMPONENT", "ISU_SUBJECT_ID", "SUBJECT", "IMPLEMENTOR_ID",
            "IMPLEMENTOR", "SUBFIELDCODE", "MAJOR_NAME", "OP_ID", "SUBFIELDNAME", "FACULTY_ID", "FACULTY", "OGNP_ID",
            "OGNP", "YEAR", "DEGREE", "SEMESTER", "LANGUAGE", "CREDITS", "LECTURE", "PRACTICE", "LAB", "EXAM", "PASS",
            "DIFF", "CP", "SRS", "ISOPTION", "SEM_INFO", "DIS_CODE", "VERSION"]
    sys_df = pd.DataFrame(columns=cols)
    return sys_df


def append_sys_df(sys_df, ep_id, subj_code,	cycle, module_id, comp, isu_subj_id, subj, imp_id, imp, sf_code, major_name,
                  op_id, sf_name, faculty_id, faculty, ognp_id, ognp, year, degree, semester, language, cred, lecture,
                  practice, lab, exam, pass_, diff, cp, srs, isoption, sem_info, dis_code, ver):
    to_append = [ep_id, subj_code, cycle, module_id, comp, isu_subj_id, subj, imp_id, imp, sf_code, major_name,
                 op_id, sf_name, faculty_id, faculty, ognp_id, ognp, year, degree, semester, language, cred, lecture,
                 practice, lab, exam, pass_, diff, cp, srs, isoption, sem_info, dis_code, ver]
    new_row = pd.Series(to_append, index=sys_df.columns)
    sys_df = sys_df.append(new_row, ignore_index=True)
    return sys_df


# generate unique code for each discipline in excel file
def generate_df_w_unique_code(in_df, sys_df=None):
    # in_df = in_df.sort_values(by=["YEAR", "SUBFIELDCODE", "SUBFIELDNAME"]).reset_index(drop=True)
    out_df = in_df.copy()
    if (sys_df is None) or sys_df.empty:
        new_sys_df = 0
        sys_df = create_sys_df()
    else:
        new_sys_df = 1
    in_df["COMPONENT"] = in_df["COMPONENT"].apply(cleanText)
    in_df["SUBJECT"] = in_df["SUBJECT"].apply(cleanText)
    in_df["YEAR"] = in_df["YEAR"].apply(str)
    sys_df["YEAR"] = sys_df["YEAR"].apply(str)
    in_df["SEM_INFO"] = "default"
    for i in in_df.index.values:
        in_df.loc[i, "SEM_INFO"] = totalUnitInfo(in_df, in_df["SUBFIELDNAME"][i], in_df["SUBJECT"][i], in_df["COMPONENT"][i], in_df["SUBJECT_CODE"][i], in_df["CYCLE"][i], in_df["YEAR"][i])
        in_df.loc[i, "DIS_CODE"] = getPos123(in_df["DEGREE"][i], in_df["COMPONENT"][i], in_df["OGNP_ID"][i], str(i + 2) + " ")
        if (in_df["SUBFIELDNAME"][i] == "Разработка программного обеспечения / Software Engineering") and (in_df["DIS_CODE"][i].split(".")[2] in ["5", "6"]):
            p34 = softwareEngineering(sys_df.loc[sys_df["DIS_CODE"].str.match(in_df.loc[i, "DIS_CODE"][:-2])], in_df.loc[i, "SEM_INFO"], in_df["DIS_CODE"][i], in_df["SUBJECT"][i],
                                      in_df["LECTURE"][i], in_df["PRACTICE"][i],
                                      in_df["LAB"][i], in_df["EXAM"][i], in_df["PASS"][i], in_df["DIFF"][i],
                                      in_df["CP"][i], in_df["IMPLEMENTOR_ID"][i], in_df["LANGUAGE"][i])
            in_df.loc[i, "DIS_CODE"] = in_df["DIS_CODE"][i][:-2] + str(p34)
        elif (in_df["DIS_CODE"][i].split(".")[0] == "06") and (in_df["DIS_CODE"][i].split(".")[1] != "0") and (in_df["DIS_CODE"][i].split(".")[2] == "3"):
            p234 = electiveModuleBachelor(sys_df.loc[sys_df["DIS_CODE"].str.match("06\.[1-7]\.3\.")], in_df.loc[i, "SEM_INFO"], in_df["DIS_CODE"][i], in_df["SUBJECT"][i],
                                          in_df["LECTURE"][i], in_df["PRACTICE"][i],
                                          in_df["LAB"][i], in_df["EXAM"][i], in_df["PASS"][i], in_df["DIFF"][i],
                                          in_df["CP"][i], in_df["IMPLEMENTOR_ID"][i], in_df["LANGUAGE"][i])
            in_df.loc[i, "DIS_CODE"] = in_df["DIS_CODE"][i][:3] + str(p234)
        else:
            p4 = getPos4(sys_df.loc[sys_df["DIS_CODE"].str.match(in_df.loc[i, "DIS_CODE"])],
                         in_df.loc[i, "SEM_INFO"], in_df["DIS_CODE"][i], in_df["SUBJECT"][i],
                         in_df["SUBFIELDNAME"][i], in_df["LECTURE"][i], in_df["PRACTICE"][i],
                         in_df["LAB"][i], in_df["EXAM"][i], in_df["PASS"][i], in_df["DIFF"][i],
                         in_df["CP"][i], in_df["IMPLEMENTOR_ID"][i], in_df["LANGUAGE"][i])

            in_df.loc[i, "DIS_CODE"] = in_df["DIS_CODE"][i] + str(p4)
        sys_df = append_sys_df(sys_df,
                               in_df["EP_ID"][i], in_df["SUBJECT_CODE"][i], in_df["CYCLE"][i], in_df["MODULE_ID"][i],
                               in_df["COMPONENT"][i], in_df["ISU_SUBJECT_ID"][i], in_df["SUBJECT"][i], in_df["IMPLEMENTOR_ID"][i],
                               in_df["IMPLEMENTOR"][i], in_df["SUBFIELDCODE"][i], in_df["MAJOR_NAME"][i], in_df["OP_ID"][i],
                               in_df["SUBFIELDNAME"][i], in_df["FACULTY_ID"][i], in_df["FACULTY"][i], in_df["OGNP_ID"][i],
                               in_df["OGNP"][i], in_df["YEAR"][i], in_df["DEGREE"][i], in_df["SEMESTER"][i], in_df["LANGUAGE"][i],
                               in_df["CREDITS"][i], in_df["LECTURE"][i], in_df["PRACTICE"][i], in_df["LAB"][i], in_df["EXAM"][i],
                               in_df["PASS"][i], in_df["DIFF"][i], in_df["CP"][i], in_df["SRS"][i], in_df["ISOPTION"][i],
                               in_df["SEM_INFO"][i], in_df["DIS_CODE"][i], in_df["YEAR"][i][-2:]).drop_duplicates().reset_index(drop=True)
        # print(i, in_df["DIS_CODE"][i], in_df["SUBJECT"][i])
    sys_df = getPos5(sys_df, new_sys_df).drop_duplicates().reset_index(drop=True)
    to_merge = sys_df[["DIS_CODE", "VERSION"]].copy()
    in_df_ver = pd.merge(in_df, to_merge, how="left", on="DIS_CODE").drop_duplicates().reset_index(drop=True)
    out_df["DIS_CODE"] = in_df_ver["DIS_CODE"] + "." + in_df_ver["VERSION"].apply(str)
    return out_df, sys_df


# generate unique code for a discipline that already exists
# TODO: пофиксить расчет кода для одной дисциплины
"""
def generate_single_unique_code(sf_code, sf_name, year, subj_degree, subj_code, subj, comp, credit_units, sys_df=None):
    if (sys_df is None) or sys_df.empty:
        new_sys_df = 0
        sys_df = create_sys_df()
    else:
        new_sys_df = 1
    comp = cleanText(comp)
    subj = cleanText(subj)
    sys_df["YEAR"] = sys_df["YEAR"].apply(str)
    year = str(year)
    dis_code = getPos123(subj_degree, sf_code, sf_name, comp)
    sem = ",".join(map(str, credit_units))
    if (sf_name == "Разработка программного обеспечения / Software Engineering") and (dis_code.split(".")[2] in ["5", "6"]):
        p34 = softwareEngineering(sys_df.loc[sys_df["DIS_CODE"].str.match(dis_code[:-2])], sem, dis_code, subj)
        dis_code = dis_code[:-2] + str(p34)
    elif (dis_code.split(".")[0] == "06") and (dis_code.split(".")[1] != "0") and (dis_code.split(".")[2] == "3"):
        p234 = electiveModuleBachelor(sys_df.loc[sys_df["DIS_CODE"].str.match("06\.[1-7]\.3\.")], sem, dis_code, subj)
        dis_code = dis_code[:3] + str(p234)
    else:
        p4 = getPos4(sys_df.loc[sys_df["DIS_CODE"].str.match(dis_code)], sem, dis_code, subj, sf_name)
        dis_code = dis_code + str(p4)
    sys_df = append_sys_df(sys_df, sf_code, sf_name, year, subj_degree, subj_code, subj, comp, sem, dis_code, year[-2:])
    sys_df = getPos5(sys_df, new_sys_df)
    dis_code = sys_df.iloc[-1, sys_df.columns.get_loc("DIS_CODE")] + "." + str(sys_df.iloc[-1, sys_df.columns.get_loc("VERSION")])
    sys_df = sys_df.drop_duplicates().reset_index(drop=True)
    return dis_code, sys_df
"""

# Example
#start_time = time.time()

# generate codes for an excel file
"""
df1 = pd.read_excel("isu_bachelor.xlsx")
# discipline_rep = pd.read_excel("discipline_bank.xlsx")
# processed_data, db = generate_df_w_unique_code(df1, discipline_rep)
processed_data, db = generate_df_w_unique_code(df1)
processed_data.to_excel("new_disciplines_test_bachelor.xlsx", index=False)
db.to_excel("discipline_bank.xlsx", index=False)
"""
"""
discipline_rep = pd.read_excel("source_files/discipline_bank.xlsx")
discipline_code, db = generate_single_unique_code("19.03.01",
                                                  "Биотехнология",
                                                  2020,
                                                  "Академический бакалавр",
                                                  32,
                                                  "Аналитическая химия и физико-химические методы анализа",
                                                  "Элективный модуль по группе направлений",
                                                  [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                  discipline_rep)
print(discipline_code)
db.to_excel("source_files/discipline_bank.xlsx", index=False)
"""
#print("--- %s seconds ---" % (time.time() - start_time))