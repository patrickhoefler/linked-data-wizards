# Linked Data Wizards

Explore and analyze Linked Data with the Linked Data Query Wizard and the Linked Data Visualization Wizard.

## Set up a local (development) instance

You can quickly set up a virtual machine containing a local instance of the Linked Data Wizards on Windows, Mac OS X, or Linux by following these simple instructions:

* Make sure that you have [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) installed.

* Run the following commands:
  ```
  git clone https://github.com/patrickhoefler/linked-data-wizards
  cd linked-data-wizards/dev
  vagrant up
  ```

After a few minutes — depending on the speed of your Internet connection — your local instance should  be ready at http://192.168.33.10:8000/.

All changes to the source code should be immediately visible after you reload the respective page in the browser.

You can stop the virtual machine at any time by running `vagrant halt` and bring it back up again with `vagrant up`.

Finally you can remove the virtual machine by running `vagrant destroy`.

## Credits

The Linked Data Wizards were initially developed at the [Know-Center](http://know-center.at/) in Graz, Austria as part of the EU-funded [CODE project](http://code-research.eu/).
