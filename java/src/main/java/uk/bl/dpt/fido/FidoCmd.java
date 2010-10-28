/**
 * 
 */
package uk.bl.dpt.fido;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;

import javax.xml.bind.JAXBException;

import uk.gov.nationalarchives.pronom.SigFile;
import uk.gov.nationalarchives.pronom.SignatureFileType;

/**
 * @author Andrew.Jackson@bl.uk
 *
 */
public class FidoCmd {

	/**
	 * @param args
	 * @throws JAXBException 
	 * @throws FileNotFoundException 
	 */
	public static void main(String[] args) throws FileNotFoundException, JAXBException {
		SignatureFileType sigFile = SigFileUtils.getLatestSigFile().getFFSignatureFile();
		SigFileUtils.writeSigFileToOutputStream(sigFile, new FileOutputStream("signaturefile.xml"));
	}

}
