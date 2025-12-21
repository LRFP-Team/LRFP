import os
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


class Detector:
	def __init__(self:object, name:str, **d:str) -> object:
		self.__name = self.__title(name) if isinstance(name, str) else ""
		self.__isEnglish = d["isEnglish"] if "isEnglish" in d and isinstance(d["isEnglish"], bool) else True
		self.__packageName = d["packageName"] if "packageName" in d and isinstance(d["packageName"], str) else ("Unknown" if self.__isEnglish else "未知")
		self.__officialLink = d["officialLink"] if "officialLink" in d and isinstance(d["officialLink"], str) else ("Unknown" if self.__isEnglish else "未知")
		self.__sourceStatus = self.__title(d["sourceStatus"]) if "sourceStatus" in d and isinstance(d["sourceStatus"], str) else ("Unknown" if self.__isEnglish else "未知")
		self.__developingPurpose = self.__title(d["developingPurpose"]) if "developingPurpose" in d and isinstance(d["developingPurpose"], str) else ("Environment Detection" if self.__isEnglish else "环境检测")
		self.__latestVersion = d["latestVersion"] if "latestVersion" in d and isinstance(d["latestVersion"], str) else ("Unknown" if self.__isEnglish else "未知")
		self.__releaseDate = d["releaseDate"] if "releaseDate" in d and isinstance(d["releaseDate"], str) else ("Unknown" if self.__isEnglish else "未知")
		self.__detectionRemark = d["detectionRemark"] if "detectionRemark" in d and isinstance(d["detectionRemark"], str) else None
		self.__figure = d["figure"] if "figure" in d and isinstance(d["figure"], str) else None
		self.__optimize()
	def __title(self:object, s:str|None) -> str|None:
		if isinstance(s, str):
			words = s.split(" ")
			for i in range(len(words)):
				if words[i]:
					words[i] = words[i][0].upper() + words[i][1:]
			return " ".join(words)
		else:
			return s
	def __optimize(self:object) -> bool:
		bRet = False
		if self.__latestVersion not in ("Unknown", "未知") and not self.__latestVersion.replace("`", "").startswith("v"):
			self.__latestVersion = "``v{0}``".format(self.__latestVersion.replace("`", ""))
			bRet = True
		for k in ("packageName", "officialLink", "developingPurpose", "sourceStatus", "latestVersion", "releaseDate"):
			key = "_Detector__{0}".format(k)
			currentValue = getattr(self, key)
			if self.__isEnglish and currentValue in ("Play 完整性检验", "环境检测", "未知"):
				setattr(self, key, {"Play 完整性检验":"Play Integrity Check", "环境检测":"Environment Detection", "未知":"Unknown"}[currentValue])
				bRet = True
			elif not self.__isEnglish and currentValue in ("Environment Detection", "Play Integrity Check", "Unknown"):
				setattr(self, key, {"Environment Detection":"环境检测", "Play Integrity Check":"Play 完整性检验", "Unknown":"未知"}[currentValue])
				bRet = True
		return bRet
	def update(self:object, **d:str) -> bool:
		bRet = False
		for key in ("packageName", "officialLink", "latestVersion", "releaseDate", "detectionRemark", "figure"):
			if key in d and isinstance(d[key], str):
				setattr(self, "_Detector__{0}".format(key), d[key])
				bRet = True
		for key in ("sourceStatus", "developingPurpose"):
			if key in d and isinstance(d[key], str):
				setattr(self, "_Detector__{0}".format(key), self.__title(d[key]))
				bRet = True
		self.__optimize()
		return bRet
	def __eq__(self:object, other:object) -> bool:
		for token in self.__name.split(" / "):
			if other == token:
				return True
		return False
	def __ne__(self:object, other:object) -> bool:
		for token in self.__name.split(" / "):
			if other == token:
				return False
		return True
	def __lt__(self:object, other:object) -> bool:
		return other > self.__name
	def __le__(self:object, other:object) -> bool:
		return other >= self.__name
	def __gt__(self:object, other:object) -> bool:
		return other < self.__name
	def __ge__(self:object, other:object) -> bool:
		return other <= self.__name
	def __str__(self:object) -> str:
		if self.__name:
			if self.__isEnglish:
				return "### {0}\n\n- **Package Name**: {1}\n- **Official Link**: {2}\n- **Source Status**: {3}\n- **Developing Purpose**: {4}\n- **Latest Version**: {5}\n- **Release Date**: {6}{7}{8}".format(	\
					self.__name, self.__packageName, self.__officialLink, self.__sourceStatus, self.__developingPurpose, self.__latestVersion, self.__releaseDate, 												\
					"\n- **Detection Remark**: {0}".format(self.__detectionRemark) if isinstance(self.__detectionRemark, str) else "", "\n{0}".format(self.__figure) if isinstance(self.__figure, str) else ""				\
				)
			else:
				return  "### {0}\n\n- **应用包名**：{1}\n- **官方链接**：{2}\n- **开源状态**：{3}\n- **开发用途**：{4}\n- **最新版本**：{5}\n- **发布日期**：{6}{7}{8}".format(		\
					self.__name, self.__packageName, self.__officialLink, self.__sourceStatus, self.__developingPurpose, self.__latestVersion, self.__releaseDate, 								\
					"\n- **注意事项**：{0}".format(self.__detectionRemark) if isinstance(self.__detectionRemark, str) else "", "\n{0}".format(self.__figure) if isinstance(self.__figure, str) else ""	\
				)
		else:
			return ""


def getTxt(filePath:str, index:int = 0) -> str: # get .txt content
	coding = ("utf-8", "gbk", "utf-16") # codings
	if 0 <= index < len(coding): # in the range
		try:
			with open(filePath, "r", encoding = coding[index]) as f:
				content = f.read()
			return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
		except (UnicodeError, UnicodeDecodeError):
			return getTxt(filePath, index + 1) # recursion
		except:
			return None
	else:
		return None # out of range

def pull(filePath:str) -> list|None:
	content = getTxt(filePath)
	if content is None:
		return None
	else:
		lines = content.splitlines()
		vectorEN, vectorZH, d = [], [], {}
		replacements = {"应用包名":"packageName", "官方链接":"officialLink", "开源状态":"sourceStatus", "开发用途":"developingPurpose", "最新版本":"latestVersion", "发布日期":"releaseDate", "注意事项":"detectionRemark"}
		flag = 0
		for line in lines:
			if "## Detectors" == line:
				flag = 1
			elif "## 检测工具" == line:
				flag = 2
			elif "name" in d and line.startswith("- **") and "**: " in line:
				separatorIndex = line.index("**: ")
				key = line[4:separatorIndex].replace(" ", "")
				if key:
					key = key[0].lower() + key[1:]
				if key in d:
					d[key] += "\n" + line[separatorIndex + 4:]
				else:
					d[key] = line[separatorIndex + 4:]
			elif "name" in d and line.startswith("- **") and "**：" in line:
				separatorIndex = line.index("**：")
				key = line[4:separatorIndex].replace(" ", "")
				if key in replacements:
					key = replacements[key]
				if key in d:
					d[key] += "\n" + line[separatorIndex + 3:]
				else:
					d[key] = line[separatorIndex + 3:]
			elif "name" in d and line.startswith("!["):
				if "figure" in d:
					d["figure"] += "\n" + line
				else:
					d["figure"] = line
			elif line.startswith("### ") or "---" == line:
				if d:
					if 1 == flag:
						d["isEnglish"] = True
						vectorEN.append(Detector(**d))
					elif 2 == flag:
						d["isEnglish"] = False
						vectorZH.append(Detector(**d))
					d.clear()
				if line.startswith("### "):
					d["name"] = line[4:]
		if d:
			if 1 == flag:
				d["isEnglish"] = True
				vectorEN.append(Detector(**d))
			elif 2 == flag:
				d["isEnglish"] = False
				vectorZH.append(Detector(**d))
		return [vectorEN, vectorZH]

def mergeDetectors(folder:str) -> list:
	if isinstance(folder, str):
		vector = []
		for root, dirs, files in os.walk(folder):
			for fileName in files:
				mainName, extName = os.path.splitext(fileName)
				if extName in (".apk", ".apks"):
					if "_v" in mainName:
						separatorIndex = mainName.index("_v")
						vector.append({"name":mainName[:separatorIndex], "latestVersion":"``v{0}``".format(mainName[separatorIndex + 2:])})
					else:
						vector.append({"name":mainName})
				elif fileName.endswith(".zip.001"):
					mainName = fileName[:-8]
					if "_v" in mainName:
						separatorIndex = mainName.index("_v")
						vector.append({"name":mainName[:separatorIndex], "latestVersion":"``v{0}``".format(mainName[separatorIndex + 2:])})
					else:
						vector.append({"name":mainName})
		return vector
	else:
		return []

def handleFolder(fd:str) -> bool:
	folder = str(fd)
	if not folder:
		return True
	elif os.path.exists(folder):
		return os.path.isdir(folder)
	else:
		try:
			os.makedirs(folder)
			return True
		except:
			return False

def push(vecEN:tuple|list, vecZH:tuple|list, filePath:str) -> bool:
	if isinstance(vecEN, (tuple, list)) and isinstance(vecZH, (tuple, list)) and isinstance(filePath, str):
		vectorEN = sorted(vecEN)
		vectorZH = sorted(vecZH)
		if handleFolder(os.path.split(filePath)[0]):
			try:
				with open(filePath, "w", encoding = "utf-8") as f:
					f.write("## Detectors\n")
					for v in vectorEN:
						if isinstance(v, Detector):
							f.write("\n{0}\n".format(v))
					f.write("---\n\n## 检测工具\n")
					for v in vectorZH:
						if isinstance(v, Detector):
							f.write("\n{0}\n".format(v))
				print("Successfully wrote {0} English item(s) and {1} Chinese item(s) to \"{2}\". ".format(len(vectorEN), len(vectorZH), filePath))
				return True
			except BaseException as e:
				print("Failed to write {0} English item(s) and {1} Chinese item(s) to \"{2}\". Exceptions are as follows. \n\t{3}".format(len(vectorEN), len(vectorZH), filePath, e))
				return False
		else:
			print("Failed to write {0} English item(s) and {1} Chinese item(s) to \"{2}\" since the parent folder is not created successfully. ".format(len(vectorEN), len(vectorZH), filePath))
			return False
	else:
		print("Parameters passed for ``push`` are invalid. ")
		return False

def main() -> int:
	inputFilePath, inputFolderPath, outputFilePath = "./README.md", ".", "./toBeReviewed.md"
	vectorEN, vectorZH = pull(inputFilePath)
	vector = mergeDetectors(inputFolderPath)
	if isinstance(vectorEN, (tuple, list)) and isinstance(vectorZH, (tuple, list)):
		for v in vector:
			if "name" in v:
				if v["name"] in vectorEN:
					v["isEnglish"] = True
					vectorEN[vectorEN.index(v["name"])].update(**v)
				else:
					v["isEnglish"] = True
					vectorEN.append(Detector(**v))
				if v["name"] in vectorZH:
					v["isEnglish"] = False
					vectorZH[vectorZH.index(v["name"])].update(**v)
				else:
					v["isEnglish"] = False
					vectorZH.append(Detector(**v))
		vectorEN.sort()
		vectorZH.sort()
		iRet = EXIT_SUCCESS if push(vectorEN, vectorZH, outputFilePath) else EXIT_FAILURE
	else:
		iRet = EOF
	print("Please press the enter key to exit ({0}). ".format(iRet))
	try:
		input()
	except:
		print()
	return iRet



if "__main__" == __name__:
	exit(main())
