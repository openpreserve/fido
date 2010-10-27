package uk.bl.dpt.fido;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.math.BigInteger;
import java.net.MalformedURLException;
import java.net.URL;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.bind.Unmarshaller;
import javax.xml.namespace.QName;
import javax.xml.transform.stream.StreamSource;

import org.apache.commons.io.IOUtils;

import uk.gov.nationalarchives.pronom.*;

/**
 * 
 * TODO When writing to XML, the JAXB bindings wrap the Signature File up in some 
 * extra XML that is not present when the file is downloaded by DROID. This could
 * be fixed by adding an appropriate XmlRootElement to the SignatureFileType, perhaps 
 * via the JAXB binding file.
 * 
 * @author Andrew Jackson
 *
 */
public class SigFileUtils {

	private static JAXBContext jc;
	
	static {
		try {
			jc  = JAXBContext.newInstance(SignatureFileType.class.getPackage().getName());
		} catch (JAXBException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	/**
	 * @return
	 */
	public static SigFile getLatestSigFile() {
		PronomService_Service pss = new PronomService_Service();
		PronomService pronomService = pss.getPronomServiceSoap();
		return pronomService.getSignatureFileV1();
	}
	
	/**
	 * @param sigFile.getFFSignatureFile()
	 * @param os
	 * @throws JAXBException
	 */
	public static void writeSigFileToOutputStream( SignatureFileType sigFile, OutputStream os ) throws JAXBException {
		//Create marshaller
		Marshaller m = jc.createMarshaller();
		m.setProperty( Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE );
		// Marshal object into file.
		// This override uses a different root element:
	    JAXBElement<SignatureFileType> rootElement = 
			new JAXBElement<SignatureFileType>(
					new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile","FFSignatureFile"), 
					SignatureFileType.class, sigFile );
		m.marshal( rootElement , os);
	}
	
	public static SignatureFileType readSigFile( File input ) throws FileNotFoundException, JAXBException {
		// Override the root element, as shown at:
		//  https://jaxb.dev.java.net/guide/_XmlRootElement_and_unmarshalling.html
		Unmarshaller u = jc.createUnmarshaller();
		JAXBElement<SignatureFileType> root = u.unmarshal(new StreamSource(input),SignatureFileType.class);
		return root.getValue();
	}
	
	/**
	 * @throws JAXBException 
	 * @throws IOException
	 */
	public static void main(String[] args) throws JAXBException, IOException {
		SigFile sigFile = getLatestSigFile();
		System.out.println("SigFile v"+sigFile.getFFSignatureFile().getVersion());
		for( FileFormatType fft : sigFile.getFFSignatureFile().getFileFormatCollection().getFileFormat()) {
			System.out.println("PUID "+fft.getPUID());
		}
		
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		writeSigFileToOutputStream(sigFile.getFFSignatureFile(),bos);
		// Turn it into a string:
		String xml = bos.toString("UTF-8");
		System.out.println(xml.substring(0, 500));
	
		// Write it to a file:
		String filename = "droid-signature_"+sigFile.getFFSignatureFile().getVersion()+".xml";
		writeSigFileToOutputStream( sigFile.getFFSignatureFile(), new FileOutputStream(filename) );
		
		// Read it back:
		SignatureFileType s2 = readSigFile( new File(filename) );
		System.out.println("Read back sigfile: "+s2.getVersion());
		
		System.out.println(downloadPronomRecordForPUID("fmt/1").substring(0, 500));
		
		// This downloads all the valid PRONOM record files.
		//downloadAllPronomFormatRecords();
	}
	
	public static void downloadAllPronomFormatRecords() {
		File outputFolder = new File("src/main/resources/uk/gov/nationalarchives/pronom/");
		outputFolder.mkdirs();
		SigFile sigFile = SigFileUtils.getLatestSigFile();
		BigInteger version = sigFile.getFFSignatureFile().getVersion();
		System.out.println("Got version "+version);
		String filename = "SignatureFile.xml";
		try {
			writeSigFileToOutputStream( sigFile.getFFSignatureFile(),
					new FileOutputStream( new File( outputFolder, filename) ) );
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//
		File fmtFolder = new File(outputFolder,"fmt"); fmtFolder.mkdir();
		File xfmtFolder = new File(outputFolder,"x-fmt"); xfmtFolder.mkdir();
		try {
			for( FileFormatType fft : sigFile.getFFSignatureFile().getFileFormatCollection().getFileFormat() ) {
				String puid = fft.getPUID();
				FileOutputStream fos = new FileOutputStream(new File(outputFolder, puid+".xml") );
				URL repurl = getPronomUrlForPUID(puid);
				System.out.println("Downloading "+repurl);
				IOUtils.copy( repurl.openStream(), fos );
				fos.flush();
				fos.getChannel().force(true);
				fos.close();
			}
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}
	
	public static URL getPronomUrlForPUID( String puid ) throws MalformedURLException {
	 return new URL("http://www.nationalarchives.gov.uk/PRONOM/"+puid+".xml");
	}
	
	public static String downloadPronomRecordForPUID( String puid ) throws IOException {
		// Validate that form is fmt/# or fmt/x-#
		URL repurl = getPronomUrlForPUID(puid);
		// Create the URL:
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		IOUtils.copy( new BufferedInputStream(repurl.openStream()), bos );
		return bos.toString();
	}

}
