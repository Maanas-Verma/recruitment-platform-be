import fitz
from user.models import Department
from .constants import UnnecessaryKeywords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def ParseResume(resume):
    doc = fitz.open(resume)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    doc.close()
    return text

def GetKeywords(resume):
    parsed_keywords = ParseResume(resume)
    unnecessary_keywords = UnnecessaryKeywords
    keywords = parsed_keywords.split()
    filtered_keywords = {keyword.lower() for keyword in keywords if keyword.lower() not in unnecessary_keywords}

    return filtered_keywords

def normalize_weights(weights):
    total_weight = sum(weights.values())

    normalized_weights = {category: weight / total_weight * 100 for category, weight in weights.items()}

    return normalized_weights


def calculate_weighted_average(scores, weights):
    return np.average(scores, weights=weights)


def DepartmentWiseAlignment(resume):
    filtered_keywords = GetKeywords(resume)
    department_weightage = {}
    all_skillset_keywords = []

    departments = Department.objects.all()

    # Iterate through departments and append their skillset keywords to the list
    for department_object in departments:
        department = department_object.name
        keywords = department_object.requirements
        all_skillset_keywords.append(' '.join(keywords))
        filtered_keywords_str = ' '.join(filtered_keywords)
        department_weights = [1] * len(all_skillset_keywords)  # Equal weights for all departments
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([filtered_keywords_str] + all_skillset_keywords)
        similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])
        weighted_averages = [calculate_weighted_average(scores, department_weights) for scores in similarity_scores]
        department_weightage[department] = weighted_averages[0]

    return normalize_weights(department_weightage)

