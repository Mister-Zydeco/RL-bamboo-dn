def try_encodings(filename):
    codecs = ['utf-8','iso-8859-1', 'latin-1']
    with open(filename, 'rb') as fh:
        bytestr = fh.read()
    st = None
    for codec in codecs:
        try:
            st = bytestr.decode(codec, 'strict')
            print(f'Codec {codec} worked!')
        except:
            print(f'Codec {codec} didn\'t work...')
   

    if st:
        lines = st.split()
        print(f'st=\n{lines[0]}...')


if __name__ == '__main__':
    try_encodings('Q')
