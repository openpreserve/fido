
package uk.gov.nationalarchives.pronom;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for SigFile complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="SigFile">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;all>
 *         &lt;element name="FFSignatureFile" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}SignatureFileType"/>
 *       &lt;/all>
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "SigFile", propOrder = {

})
public class SigFile {

    @XmlElement(name = "FFSignatureFile", required = true)
    protected SignatureFileType ffSignatureFile;

    /**
     * Gets the value of the ffSignatureFile property.
     * 
     * @return
     *     possible object is
     *     {@link SignatureFileType }
     *     
     */
    public SignatureFileType getFFSignatureFile() {
        return ffSignatureFile;
    }

    /**
     * Sets the value of the ffSignatureFile property.
     * 
     * @param value
     *     allowed object is
     *     {@link SignatureFileType }
     *     
     */
    public void setFFSignatureFile(SignatureFileType value) {
        this.ffSignatureFile = value;
    }

}
