exec { 'update':
    command => "sudo apt-get update",
    path => "/usr/bin/",
    before => Class['clerk'],
}

class { 'clerk': 
    hostname => '10.5.36.32',
    require => Exec['update'],
}


