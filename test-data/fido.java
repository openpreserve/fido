// Main program to parse the Trace log files
import java.io.* ;
import java.util.* ;


class CrvDefine
{
    public String type = "ignore" ;
    public String name = "" ;
    public String str1 = null ;
    public String str2 = null ;
}


class RawCurve
{
    public String type ;
    public FileWriter fw ;
    public BufferedWriter bw ;
    public long lastTime ;

    RawCurve( String type, String myDir, String cName ) throws Exception
    {
        this.type     = type ;
        this.fw       = new FileWriter( myDir + cName.replace( ' ', '_' ) ) ;
        this.bw       = new BufferedWriter( this.fw ) ;
        this.lastTime = -999999 ;
    }
}


class ParseNode extends Thread
{
    String  myDir   ;
    String  node    ;
    Vector  crvDefs ;
    String  status  ;

    long    startTime, stopTime = -1 ;
    HashMap rawCrvs = new HashMap() ;

    ParseNode( String dataDir, String node, Vector crvDefs )
    {
        this.myDir   = dataDir + "/" + node + "/" ;
        this.node    = node    ;
        this.crvDefs = crvDefs ;
        this.status  = node + ":" ;
    }

    public void run()
    {
        try
        {
            String str = myDir + node + ".log" ;

            // move the log file away
            String  cmd = "/bin/mv " + str + " " + myDir + ".." ;
            Process sys = Runtime.getRuntime().exec( cmd ) ;
            sys.waitFor() ;

            if ( sys.exitValue() != 0 )
            {
                status = status + "\n" + "Failed to \"" + cmd + "\"" ;
                return ;
            }

            // clear the directory
            cmd = "/bin/rm " + myDir + "*" ;
            sys = Runtime.getRuntime().exec( cmd ) ;
            sys.waitFor() ;

            // move back the log file
            cmd = "/bin/mv " + myDir + "../" + node + ".log " + myDir ;
            sys = Runtime.getRuntime().exec( cmd ) ;
            sys.waitFor() ;

            if ( sys.exitValue() != 0 )
            {
                status = status + "\n" + "Failed to \"" + cmd + "\"" ;
                return ;
            }

            // open the log file
            FileReader     fr = new FileReader    ( str ) ;
            BufferedReader br = new BufferedReader( fr  ) ;

            // skip the header
            skipHeader( br ) ;

            // parse the file
            while ( ( str = br.readLine() ) != null )
            {
                if ( str.equals( "" ) ) continue ;           // skip empty lines

                long   newTime = getTime( str ) ;
                String txt     = getText( br, str ) ;

                if ( stopTime == -1 ) stopTime = newTime ;

                boolean match = false ;
                for ( int ic=0 ; ic<crvDefs.size() ; ic++ )
                {
                    CrvDefine crv = (CrvDefine) crvDefs.elementAt( ic ) ;

                    if ( txt.matches( crv.str1 ) )
                    {
                        match = true ;

                        if      ( crv.type.equals( "ignore" ) ) break ;
                        else if ( crv.type.equals( "block"  ) )
                            GoUp  ( crv.name, newTime ) ;
                        else if ( crv.type.equals( "spike"  ) )
                            Spike ( crv.name, newTime ) ;
                        else if ( crv.type.equals( "toggle" ) )
                            Toggle( crv.name, newTime ) ;
                    }
                    else if ( crv.type.equals( "block" ) &&
                              txt.matches( crv.str2    )    )
                    {
                        match = true ;

                        GoDown( crv.name, newTime ) ;
                    }
                }

                // also write out the un-defined curves
                if ( ! match )
                {
                    if      ( txt.startsWith( "sched: " ) )
                    {
                        String[] xxx = txt.split( " " ) ;
                        String   pre = "pid" + xxx[1].split( "=" )[1] ;
                        String   nxt = "pid" + xxx[2].split( "=" )[1] ;
                        GoDown( pre,                newTime ) ;
                        GoUp  ( nxt,                newTime ) ;
                    }
                    else if ( txt.startsWith( "exit " ) )
                        GoDown( txt.substring( 5 ), newTime ) ;
                    else if ( txt.startsWith( "enter " ) )
                        GoUp  ( txt.substring( 6 ), newTime ) ;
                    else
                        Spike ( txt, newTime ) ;
                }

                startTime = newTime ;
            }
            br.close() ;
            fr.close() ;

            // write the summary, close the files
            str = myDir + node + ".crv" ;
            FileWriter     fw = new FileWriter    ( str ) ;
            BufferedWriter bw = new BufferedWriter( fw  ) ;

            bw.write( "# Time range" ) ;
            bw.newLine() ;
            bw.write( stopTime + " " + startTime ) ;
            bw.newLine() ;
            bw.newLine() ;

            bw.write( "# Curve list" ) ;
            bw.newLine() ;

            String[] cNames=(String[]) rawCrvs.keySet().toArray(new String[0]) ;
            for ( int ic=0 ; ic<cNames.length ; ic++ )
            {
                bw.write( cNames[ ic ].replace( ' ', '_' ) ) ;
                bw.newLine() ;

                RawCurve crv = (RawCurve) rawCrvs.get( cNames[ ic ] ) ;
                if ( crv.lastTime != -999999 )   // block/toggle without raising
                {
                    crv.bw.write( (stopTime-crv.lastTime ) + " " +
                                  (crv.lastTime-startTime) ) ;
                    crv.bw.newLine() ;
                }

                crv.bw.close() ;
                crv.fw.close() ;
            }
            bw.close() ;
            fw.close() ;
        }
        catch( Exception e )
        {
            status = status + "\n" + e ;
            return ;
        }

        status += "  successfully parsed." ;
    }

    void skipHeader( BufferedReader br ) throws Exception
    {
        String txt ;
        try
        {
            while ( ( txt = br.readLine() ) != null )
            {
                if ( txt.startsWith( "          timeStamp" ) )
                {
                    txt = br.readLine() ;
                    txt = br.readLine() ;
                    break ;
                }
            }
        }
        catch( Exception e )
        {
            throw e ;
        }
    }

    long getTime( String str ) throws Exception
    {
        long newTime ;

        try
        {
            newTime = Long.parseLong( str.substring(  0, 19 ).trim() ) ;
        }
        catch( Exception e )
        {
            throw e ;
        }

        return newTime ;
    }

    String getText( BufferedReader br, String str ) throws Exception
    {
        String txt ;

        try
        {
            if ( str.length() > 32 ) txt = str.substring( 32 ) ;
            else                     txt = br.readLine()       ;
        }
        catch( Exception e )
        {
            throw e ;
        }

        return txt ;
    }

    void GoUp( String cName, long newTime ) throws Exception
    {
        RawCurve crv = (RawCurve) rawCrvs.get( cName ) ;
        if ( crv == null )
        {
            crv = new RawCurve( "block", myDir, cName ) ;
            rawCrvs.put( cName, crv ) ;
        }

        if ( crv.lastTime == -999999 )          // a block without trailing edge
            crv.bw.write( "0 " + (stopTime-newTime) ) ;
        else                                // write out the block, clear memory
        {
            crv.bw.write( (stopTime-crv.lastTime) + " " +
                          (crv.lastTime-newTime ) ) ;

            crv.lastTime = -999999 ;
        }

        crv.bw.newLine() ;
    }

    void GoDown( String cName, long newTime ) throws Exception
    {
        RawCurve crv = (RawCurve) rawCrvs.get( cName ) ;
        if ( crv == null )
        {
            crv = new RawCurve( "block", myDir, cName ) ;
            rawCrvs.put( cName, crv ) ;
        }

        crv.lastTime = newTime ;                   // remember the trailing edge
    }

    void Spike( String cName, long newTime ) throws Exception
    {
        RawCurve crv = (RawCurve) rawCrvs.get( cName ) ;
        if ( crv == null )
        {
            crv = new RawCurve( "spike", myDir, cName ) ;
            rawCrvs.put( cName, crv ) ;
        }

        crv.bw.write( (stopTime-newTime) + " 0" ) ;
        crv.bw.newLine() ;
    }

    void Toggle( String cName, long newTime ) throws Exception
    {
        RawCurve crv = (RawCurve) rawCrvs.get( cName ) ;
        if ( crv == null )
        {
            crv = new RawCurve( "toggle", myDir, cName ) ;
            rawCrvs.put( cName, crv ) ;
        }

        if ( crv.lastTime == -999999 )   // 1st time, remember the trailing edge
            crv.lastTime = newTime ;
        else                      // 2nd time, write out the block, clear memory
        {
            crv.bw.write( (stopTime-crv.lastTime) + " " +
                          (crv.lastTime-newTime ) ) ;
            crv.bw.newLine() ;

            crv.lastTime = -999999 ;
        }
    }
}


public class JTraceParse
{
    public static void main( String args[] )
    {
        String dataDir  = "" ;
        Vector nodeList = new Vector() ;
        Vector crvDefs  = new Vector() ;

        int    maxProc  = 3 ;

        if ( args.length == 0 )
        {
            System.out.println( "Usage:  java  JTraceParse  \"config file\"" ) ;
            System.exit( 0 ) ;
        }

        try
        {
            FileReader     fr = new FileReader    ( args[0] ) ;
            BufferedReader br = new BufferedReader( fr      ) ;

            String txt ;
            int    block = 0 ;
            while ( ( txt = br.readLine() ) != null )
            {
                if      ( txt.equals( "" ) ) continue ;
                else if ( txt.equals( "# data directory" ) )
                {
                    dataDir = br.readLine() ;
                }
                else if ( txt.startsWith( "# max number of" ) )
                {
                    maxProc = Integer.parseInt( br.readLine() ) ;
                }
                else if ( txt.equals( "# raw curves" ) )
                {
                    block = 1 ;
                }
                else if ( block == 1 )
                {
                    CrvDefine crvDef = new CrvDefine() ;
                    crvDef.type = txt.substring( 0, txt.indexOf( ":" ) ) ;

                    if ( ! txt.startsWith( "ignore:" ) )         // get the name
                        crvDef.name = txt.substring( txt.indexOf( ": " ) + 2 ) ;

                    if ( ! txt.startsWith( "block:" ) )
                        crvDef.str1 = br.readLine() ;
                    else
                    {
                        txt = br.readLine() ;
                        if ( txt.startsWith( "up=" ) )
                            crvDef.str1 = txt.substring( 3 ) ;
                        else
                            crvDef.str2 = txt.substring( 5 ) ;

                        txt = br.readLine() ;
                        if ( txt.startsWith( "down=" ) )
                            crvDef.str2 = txt.substring( 5 ) ;
                        else
                            crvDef.str1 = txt.substring( 3 ) ;
                    }

                    crvDefs.add( crvDef ) ;
                }
            }
            br.close() ;
            fr.close() ;

            System.out.println( "Max # of simultaneous processing threads:  " +
                                maxProc ) ;

            fr = new FileReader    ( dataDir + "/nodelist" ) ;
            br = new BufferedReader( fr                    ) ;
            while ( ( txt = br.readLine() ) != null )
            {
                if ( txt.equals( "nodelist" ) ) continue ;

                if ( nodeList.size() == maxProc ) // wait till some threads exit
                {
                    while( true )
                    {
                        int ip = 0 ;
                        while ( ip < nodeList.size() )
                        {
                            ParseNode p = (ParseNode) nodeList.elementAt( ip ) ;

                            if ( p.isAlive() ) ip++ ;
                            else
                            {
                                // success or not ?
                                System.out.println( p.status ) ;

                                nodeList.remove( ip ) ;
                            }
                        }

                        if ( nodeList.size() == maxProc )
                        {
                            try
                            {
                                Thread.sleep( 3000 ) ;
                            }
                            catch( Exception e )
                            {
                            }
                        }
                        else
                            break ;
                    }
                }

                ParseNode p = new ParseNode( dataDir, txt, crvDefs ) ;
                p.start() ;

                nodeList.add( p ) ;
            }
            br.close() ;
            fr.close() ;
        }
        catch( Exception e )
        {
            e.printStackTrace() ;
        }

        while( true )
        {
            int ip = 0 ;
            while ( ip < nodeList.size() )
            {
                ParseNode p = (ParseNode) nodeList.elementAt( ip ) ;

                if ( p.isAlive() ) ip++ ;
                else
                {
                    // success or not ?
                    System.out.println( p.status ) ;

                    nodeList.remove( ip ) ;
                }
            }

            if ( nodeList.size() > 0 )
            {
                try
                {
                    Thread.sleep( 3000 ) ;
                }
                catch( Exception e )
                {
                }
            }
            else
                break ;
        }
    }
}

