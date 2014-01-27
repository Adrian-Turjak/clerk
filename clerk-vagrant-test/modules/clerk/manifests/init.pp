class clerk (
    $pythonversion  = "2.7.4",
    $pipversion     = "1.4.1",
    $djangoversion  = "1.6",
    $djangorestversion = "2.3.9",
    $appname        = 'Clerk',
    $apppath        = "/vagrant",
    $managepath     = "/vagrant/Clerk",
    $aptgetdir      = "/usr/bin/",
    $hostname       = 'localhost',    
    $dbname         = 'clerk',
    $dbuser         = 'admin',
    $dbpassword     = 'password',
    $dbhost         = 'localhost',
){
    class { '::mysql::server':
        root_password    => 'strongpassword',
        override_options => { 'mysqld' => { 'max_connections' => '1024' } }
    }
    
    mysql::db { $dbname:
        user     => $dbuser,
        password => $dbpassword,
        host     => $dbhost,
        grant    => ['ALL'],
        before   => Exec['syncdb'],
    }

    class { 'apache': }
    
    class { 'apache::mod::wsgi': }
    
    apache::vhost { $hostname:
        port                        => '80',
        docroot                     => '/var/www/Clerk',
        wsgi_daemon_process         => 'wsgi',
        wsgi_daemon_process_options =>
        { processes => '2', threads => '15', display-name => '%{GROUP}' },
        wsgi_process_group          => 'wsgi',
        wsgi_script_aliases         => { '/' => '/var/www/clerk.wsgi',
                                         '/' => '/var/www/artifice.wsgi' },
        aliases                     => [ { alias => '/static', path => '/var/www/Clerk/static' } ],
        directories                 => [ { path => '/var/www/Clerk/static', allow => 'from all' } ],
        before                      => Exec['staticfiles']
    }

    file { 'clerk.wsgi':
        ensure  => file,
        path    => '/var/www/clerk.wsgi',
        content => template("clerk/wsgi.erb"),
    }

    file { 'settings':
        ensure  => file,
        path    => '/vagrant/Clerk/Clerk/settings.py',
        content => template("clerk/settings.erb"),
    }

    exec {'syncdb':
        command => '/usr/bin/python manage.py syncdb --noinput',
        cwd    => "$managepath",
        require => Class['clerk::django::install'],
    }

    exec {'staticfiles':
        command => '/usr/bin/python manage.py collectstatic --noinput',
        cwd     => "$managepath",
        require => Class['clerk::django::install'],
    }

    include clerk::django
}
