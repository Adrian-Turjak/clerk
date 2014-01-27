class artifice (
    $pythonversion  = "2.7.4",
    $pipversion     = "1.4.1",
    $appname        = 'artifice_api',
    $apppath        = "/vagrant/Artifice",
    $managepath     = "/vagrant/Artifice",
    $aptgetdir      = "/usr/bin/",
    $hostname       = 'localhost',    
    $dbname         = 'artifice',
    $dbuser         = 'admin',
    $dbpassword     = 'password',
    $dbhost         = 'localhost',
){
    file { 'artifice.wsgi':
        ensure  => file,
        path    => '/var/www/artifice.wsgi',
        content => template("artifice/wsgi.erb"),
    }

    # include artifice::core
    include artifice::api
}
