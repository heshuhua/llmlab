"""
wo module. contains function words_occur()"""
# interface functions
def words_occur():
    """ words_occur -count words in a file  """
    
    # Prompt user for the name of the file 
    file_name=input("Enter the name of the file:")
    file=open(file_name,'r')
    word_list=file.read().split()
    file.close()
    occurs_dict={}
    for word in word_list:
        occurs_dict[word]=occurs_dict.get(word,0)+1
    print(f"File {file_name} has {len(word_list)} words.")
    print(occurs_dict)
if __name__=='__main__':
    words_occur()