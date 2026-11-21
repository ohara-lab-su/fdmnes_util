"""Write convolution job inputs corresponding to allsite output spectra."""
from pathlib import Path
import re
from .write_fdmfile import WriteFdmfile
class WriteFdmConvolutionInputs:
    def write(self,filout,output_dir='.'):
        prefix=Path(filout).name
        source=Path(filout).parent
        candidates=sorted(x for x in source.glob(prefix+'_*.txt')
                          if re.fullmatch(re.escape(prefix)+r'_\d+\.txt',x.name))
        directory=Path(output_dir);directory.mkdir(exist_ok=True,parents=True)
        inputs=[]
        for index,spectrum in enumerate(candidates,1):
            name=f'conv_{index}.inp'
            text=('\n Filout\n   '+prefix+'\n\n Calculation\n   '+spectrum.name
                  +'\n\n Conv_out\n   '+spectrum.stem+'_conv.txt'
                  +'\n\n Convolution\n\nEND\n')
            (directory/name).write_text(text)
            inputs.append(name)
        WriteFdmfile().write(inputs,directory/'fdmfile.txt')
        return inputs
