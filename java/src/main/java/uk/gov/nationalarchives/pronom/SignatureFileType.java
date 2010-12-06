
package uk.gov.nationalarchives.pronom;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;
import javax.xml.datatype.XMLGregorianCalendar;


/**
 * <p>Java class for SignatureFileType complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="SignatureFileType">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;all>
 *         &lt;element name="InternalSignatureCollection">
 *           &lt;complexType>
 *             &lt;complexContent>
 *               &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *                 &lt;choice maxOccurs="unbounded" minOccurs="0">
 *                   &lt;element name="InternalSignature" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}InternalSignatureType"/>
 *                 &lt;/choice>
 *               &lt;/restriction>
 *             &lt;/complexContent>
 *           &lt;/complexType>
 *         &lt;/element>
 *         &lt;element name="FileFormatCollection">
 *           &lt;complexType>
 *             &lt;complexContent>
 *               &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *                 &lt;choice maxOccurs="unbounded" minOccurs="0">
 *                   &lt;element name="FileFormat" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormatType"/>
 *                 &lt;/choice>
 *               &lt;/restriction>
 *             &lt;/complexContent>
 *           &lt;/complexType>
 *         &lt;/element>
 *       &lt;/all>
 *       &lt;attribute name="Version" use="required" type="{http://www.w3.org/2001/XMLSchema}positiveInteger" />
 *       &lt;attribute name="DateCreated" use="required" type="{http://www.w3.org/2001/XMLSchema}dateTime" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "SignatureFileType", propOrder = {

})
public class SignatureFileType {

    @XmlElement(name = "InternalSignatureCollection", required = true)
    protected SignatureFileType.InternalSignatureCollection internalSignatureCollection;
    @XmlElement(name = "FileFormatCollection", required = true)
    protected SignatureFileType.FileFormatCollection fileFormatCollection;
    @XmlAttribute(name = "Version", required = true)
    @XmlSchemaType(name = "positiveInteger")
    protected BigInteger version;
    @XmlAttribute(name = "DateCreated", required = true)
    @XmlSchemaType(name = "dateTime")
    protected XMLGregorianCalendar dateCreated;

    /**
     * Gets the value of the internalSignatureCollection property.
     * 
     * @return
     *     possible object is
     *     {@link SignatureFileType.InternalSignatureCollection }
     *     
     */
    public SignatureFileType.InternalSignatureCollection getInternalSignatureCollection() {
        return internalSignatureCollection;
    }

    /**
     * Sets the value of the internalSignatureCollection property.
     * 
     * @param value
     *     allowed object is
     *     {@link SignatureFileType.InternalSignatureCollection }
     *     
     */
    public void setInternalSignatureCollection(SignatureFileType.InternalSignatureCollection value) {
        this.internalSignatureCollection = value;
    }

    /**
     * Gets the value of the fileFormatCollection property.
     * 
     * @return
     *     possible object is
     *     {@link SignatureFileType.FileFormatCollection }
     *     
     */
    public SignatureFileType.FileFormatCollection getFileFormatCollection() {
        return fileFormatCollection;
    }

    /**
     * Sets the value of the fileFormatCollection property.
     * 
     * @param value
     *     allowed object is
     *     {@link SignatureFileType.FileFormatCollection }
     *     
     */
    public void setFileFormatCollection(SignatureFileType.FileFormatCollection value) {
        this.fileFormatCollection = value;
    }

    /**
     * Gets the value of the version property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getVersion() {
        return version;
    }

    /**
     * Sets the value of the version property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setVersion(BigInteger value) {
        this.version = value;
    }

    /**
     * Gets the value of the dateCreated property.
     * 
     * @return
     *     possible object is
     *     {@link XMLGregorianCalendar }
     *     
     */
    public XMLGregorianCalendar getDateCreated() {
        return dateCreated;
    }

    /**
     * Sets the value of the dateCreated property.
     * 
     * @param value
     *     allowed object is
     *     {@link XMLGregorianCalendar }
     *     
     */
    public void setDateCreated(XMLGregorianCalendar value) {
        this.dateCreated = value;
    }


    /**
     * <p>Java class for anonymous complex type.
     * 
     * <p>The following schema fragment specifies the expected content contained within this class.
     * 
     * <pre>
     * &lt;complexType>
     *   &lt;complexContent>
     *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
     *       &lt;choice maxOccurs="unbounded" minOccurs="0">
     *         &lt;element name="FileFormat" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormatType"/>
     *       &lt;/choice>
     *     &lt;/restriction>
     *   &lt;/complexContent>
     * &lt;/complexType>
     * </pre>
     * 
     * 
     */
    @XmlAccessorType(XmlAccessType.FIELD)
    @XmlType(name = "", propOrder = {
        "fileFormat"
    })
    public static class FileFormatCollection {

        @XmlElement(name = "FileFormat")
        protected List<FileFormatType> fileFormat;

        /**
         * Gets the value of the fileFormat property.
         * 
         * <p>
         * This accessor method returns a reference to the live list,
         * not a snapshot. Therefore any modification you make to the
         * returned list will be present inside the JAXB object.
         * This is why there is not a <CODE>set</CODE> method for the fileFormat property.
         * 
         * <p>
         * For example, to add a new item, do as follows:
         * <pre>
         *    getFileFormat().add(newItem);
         * </pre>
         * 
         * 
         * <p>
         * Objects of the following type(s) are allowed in the list
         * {@link FileFormatType }
         * 
         * 
         */
        public List<FileFormatType> getFileFormat() {
            if (fileFormat == null) {
                fileFormat = new ArrayList<FileFormatType>();
            }
            return this.fileFormat;
        }

    }


    /**
     * <p>Java class for anonymous complex type.
     * 
     * <p>The following schema fragment specifies the expected content contained within this class.
     * 
     * <pre>
     * &lt;complexType>
     *   &lt;complexContent>
     *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
     *       &lt;choice maxOccurs="unbounded" minOccurs="0">
     *         &lt;element name="InternalSignature" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}InternalSignatureType"/>
     *       &lt;/choice>
     *     &lt;/restriction>
     *   &lt;/complexContent>
     * &lt;/complexType>
     * </pre>
     * 
     * 
     */
    @XmlAccessorType(XmlAccessType.FIELD)
    @XmlType(name = "", propOrder = {
        "internalSignature"
    })
    public static class InternalSignatureCollection {

        @XmlElement(name = "InternalSignature")
        protected List<InternalSignatureType> internalSignature;

        /**
         * Gets the value of the internalSignature property.
         * 
         * <p>
         * This accessor method returns a reference to the live list,
         * not a snapshot. Therefore any modification you make to the
         * returned list will be present inside the JAXB object.
         * This is why there is not a <CODE>set</CODE> method for the internalSignature property.
         * 
         * <p>
         * For example, to add a new item, do as follows:
         * <pre>
         *    getInternalSignature().add(newItem);
         * </pre>
         * 
         * 
         * <p>
         * Objects of the following type(s) are allowed in the list
         * {@link InternalSignatureType }
         * 
         * 
         */
        public List<InternalSignatureType> getInternalSignature() {
            if (internalSignature == null) {
                internalSignature = new ArrayList<InternalSignatureType>();
            }
            return this.internalSignature;
        }

    }

}
