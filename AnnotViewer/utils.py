#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

from lxml import etree
import json
import re

##Need to parse XMI file into multiple sections
##  Annotations
##  From annotations get covered text in word tokens
##  From annotations get UMLSConcept

def getSofaString(doc,names):
    for sofa in doc.xpath('//cas:Sofa/@sofaString',namespaces=names):
        finalSofa = sofa

    return finalSofa


def getCoveredText(doc,begin,end,names,sofa):
    coveredText = sofa[int(begin):int(end)]
    return coveredText


def getUMLSConcept(doc,names,umlsIDs):

    concepts = []
    i = 0;
    for ss in doc.xpath('//refsem:UmlsConcept',namespaces=names):
        i += 1
        if ss.xpath('@xmi:id',namespaces=names)[0] in umlsIDs:
            cui = ss.attrib['cui']
            prefText = ss.attrib['preferredText']
            if not any(d['cui'] == cui for d in concepts):
                concepts.append({'id' : i, 'cui' : cui, 'prefText' : prefText})

    return concepts

def getAnnotations(annotationTypes, names,doc,sofaString):
    
    annotList = []
    for annotationType in annotationTypes:
        for ss in doc.xpath('//textsem:' + annotationType ,namespaces=names):
            annotid = int(ss.attrib['{http://www.omg.org/XMI}id'])
            begin = int(ss.attrib['begin'])
            end = int(ss.attrib['end'])
            polarity = "NO" if int(ss.attrib['polarity']) <> -1  else "YES"
            generic = "NO" if ss.attrib['generic'] == 'false' else "YES"
            historyOf = "NO" if int(ss.attrib['historyOf']) == 0 else "YES"
            coveredText = getCoveredText(doc,begin,end,names,sofaString)        
            umlsIDs = ss.attrib['ontologyConceptArr'].split(' ')
            umlsconcepts = getUMLSConcept(doc,names,umlsIDs)
            
            annotList.append({'annotID': annotid, 'ct' : coveredText, 'bA' : begin, 'eA' : end, 'negated' : polarity, 'generic' : generic, 'historyOf' : historyOf, 'annotationType' : annotationType, 'userdata' : umlsconcepts})
    
    return annotList

