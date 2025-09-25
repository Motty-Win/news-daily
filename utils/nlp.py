from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering


def cluster_by_title(items, n_clusters=None, distance_threshold=0.6):
    titles = [it["title"] for it in items]
    if len(titles) <= 3:
        return [list(range(len(titles)))]
    vec = TfidfVectorizer(min_df=1).fit_transform(titles)
    dist = 1 - (vec * vec.T).toarray()
    if n_clusters is None:
        model = AgglomerativeClustering(
            metric="precomputed",
            linkage="average",
            distance_threshold=distance_threshold,
            n_clusters=None,
        )
    else:
        model = AgglomerativeClustering(
            metric="precomputed", linkage="average", n_clusters=n_clusters
        )
    labels = model.fit_predict(dist)
    clusters = {}
    for idx, lb in enumerate(labels):
        clusters.setdefault(lb, []).append(idx)
    return list(clusters.values())
