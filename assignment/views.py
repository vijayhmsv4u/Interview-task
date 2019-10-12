from django.shortcuts import render
from rest_framework import response, status, decorators
from django.conf import settings
import os
import pandas as pd


@decorators.api_view(['GET'])
def search(request):
    word= request.GET.get("word",None)
    '''
     If dataset file not found then raise exception

    '''
    if not os.path.isfile(settings.UNIGRAM_PATH):
        return response.Response({
                    "data": None,
                    "message":"Unigram File Not Found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
    '''
    if input search word is not alphabetic then raise exception

    '''
    if not word.isalpha():
        return response.Response({
                    "data": None,
                    "message":"Input should not have special characters"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    if word:
        filter_unigrams={}
        unigram_data= pd.read_csv(settings.UNIGRAM_PATH, index_col=0) # read data from corpus file

        unigram_data.dropna(inplace=True)
        unigram_data= unigram_data.filter(like=word,axis=0)           # filter data from corpus

        max_word_len= len(sorted(unigram_data.index[1:], key=len)[-1])
        for unigram,unigram_value in unigram_data.to_dict()["count"].items():
            if type(unigram)==str and word in unigram:
                word_length_rank=max_word_len-len(unigram)
                index_rank= 25-unigram.find(word)
                rank= (unigram_value+word_length_rank+index_rank)/3
                if rank not in filter_unigrams.keys():
                    filter_unigrams[rank]=[]
                
                filter_unigrams[rank].append(unigram)
        count=0
        sorted_unigrams=[]
        unigrams_count=list(filter_unigrams.keys())
        unigrams_count.sort(reverse=True)
        for unigram in unigrams_count:
            for uni in filter_unigrams[unigram]:
                if count<25:
                    sorted_unigrams.append(uni)
                    count+=1
                else:
                    break
        if word in sorted_unigrams:
            sorted_unigrams.remove(word)
            sorted_unigrams.insert(0, word)
            sorted_unigrams= sorted_unigrams[:25]
        return response.Response({
                    "data": sorted_unigrams,
                    "message":"Data Retrieved SuccessFully"
                },
                status=status.HTTP_200_OK
            )    
    else:
        return response.Response({
            "data": None,
            "message":"Enter Valid Input"
        },
        status=status.HTTP_400_BAD_REQUEST
    ) 