    # feature_extraction.py

import re
import socket
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def extract_features(url):
    features = {}
    
    try:
        response = requests.get(url, timeout=5)
        content = response.text
    except:
        content = ""
    
    parsed = urlparse(url)
    hostname = parsed.netloc
    path = parsed.path

    # Easy-to-extract features
    #features['length_url'] = len(url)
    features['length_hostname'] = len(hostname)
    features['ip'] = 1 if is_ip_address(hostname) else 0
    features['nb_slash'] = url.count('/')
    features['nb_www'] = 1 if "www." in url else 0
    features['ratio_digits_url'] = sum(c.isdigit() for c in url) / len(url)
    
    # HTML-based features
    soup = BeautifulSoup(content, "html.parser")
    hyperlinks = soup.find_all('a')
    features['nb_hyperlinks'] = len(hyperlinks)
    features['phish_hints'] = sum(1 for tag in soup.find_all()
                                  if any(term in str(tag).lower() for term in ['login', 'verify', 'signin', 'bank']))
    
    # Longest/shortest/avg word in path
    path_words = re.split(r'[^a-zA-Z0-9]', path)
    path_words = [w for w in path_words if w]

    if path_words:
        word_lengths = [len(w) for w in path_words]
        features['longest_word_path'] = max(word_lengths)
        features['shortest_word_path'] = min(word_lengths)
        features['avg_word_path'] = sum(word_lengths) / len(word_lengths)
    else:
        features['longest_word_path'] = 0
        features['shortest_word_path'] = 0
        features['avg_word_path'] = 0

    # Words from full URL (for length calculations)
    all_words = re.split(r'[^a-zA-Z0-9]', url)
    all_words = [w for w in all_words if w]
    
    if all_words:
        word_lengths = [len(w) for w in all_words]
        features['length_words_raw'] = len(all_words)
        features['longest_words_raw'] = max(word_lengths)
    else:
        features['length_words_raw'] = 0
        features['longest_words_raw'] = 0

    # Ratios (external hyperlinks etc.)
    int_links = 0
    ext_links = 0
    for tag in hyperlinks:
        href = tag.get('href', '')
        if hostname in href or href.startswith('/'):
            int_links += 1
        elif href.startswith('http'):
            ext_links += 1

    total_links = int_links + ext_links
    features['ratio_extHyperlinks'] = ext_links / total_links if total_links else 0
    features['ratio_extRedirection'] = count_external_redirection(soup, hostname)
    features['ratio_intHyperlinks'] = int_links / total_links if total_links else 0

    return features


def is_ip_address(hostname):
    try:
        socket.inet_aton(hostname)
        return True
    except:
        return False

def count_external_redirection(soup, hostname):
    redir_links = 0
    for tag in soup.find_all('a'):
        href = tag.get('href', '')
        if href.startswith("http") and hostname not in href:
            redir_links += 1
    return redir_links / max(len(soup.find_all('a')), 1)
